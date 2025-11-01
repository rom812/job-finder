"""
Comprehensive tests for Agent 4: Smart Matcher
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from agents.matcher import SmartMatcher
from models.models import CVAnalysis, Job, CompanyInsights, JobMatch


class TestCosineSimiliarity:
    """Test the cosine similarity calculation"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    def test_identical_vectors(self):
        """Test that identical vectors have similarity of 1.0"""
        vec1 = [1.0, 2.0, 3.0, 4.0]
        vec2 = [1.0, 2.0, 3.0, 4.0]

        similarity = self.matcher._cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(1.0, abs=0.001)

    def test_opposite_vectors(self):
        """Test that opposite vectors have similarity of -1.0"""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]

        similarity = self.matcher._cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(-1.0, abs=0.001)

    def test_orthogonal_vectors(self):
        """Test that perpendicular vectors have similarity of 0.0"""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        similarity = self.matcher._cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(0.0, abs=0.001)

    def test_zero_vector(self):
        """Test that zero vectors return 0.0 (avoid division by zero)"""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        similarity = self.matcher._cosine_similarity(vec1, vec2)

        assert similarity == 0.0

    def test_similar_vectors(self):
        """Test similar (but not identical) vectors"""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.1, 2.1, 2.9]

        similarity = self.matcher._cosine_similarity(vec1, vec2)

        # Should be close to 1.0 but not exactly
        assert 0.95 < similarity < 1.0


class TestSkillOverlap:
    """Test skill overlap calculation"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    def test_perfect_overlap(self):
        """Test when all CV skills are in job description"""
        cv_skills = ["Python", "Docker", "PostgreSQL"]
        job_desc = "We need a developer with Python, Docker, and PostgreSQL experience"

        overlap, missing = self.matcher._calculate_skill_overlap(cv_skills, job_desc)

        assert len(overlap) == 3
        assert "Python" in overlap
        assert "Docker" in overlap
        assert "PostgreSQL" in overlap

    def test_partial_overlap(self):
        """Test when only some CV skills match"""
        cv_skills = ["Python", "Java", "Ruby"]
        job_desc = "Looking for Python and JavaScript developer"

        overlap, missing = self.matcher._calculate_skill_overlap(cv_skills, job_desc)

        assert "Python" in overlap
        assert "Java" not in overlap
        assert "JavaScript" in missing

    def test_no_overlap(self):
        """Test when no CV skills match"""
        cv_skills = ["Python", "Django"]
        job_desc = "Looking for Java and Spring Boot developer"

        overlap, missing = self.matcher._calculate_skill_overlap(cv_skills, job_desc)

        assert len(overlap) == 0
        assert "Java" in missing

    def test_case_insensitive(self):
        """Test that skill matching is case-insensitive"""
        cv_skills = ["Python", "DOCKER"]
        job_desc = "Experience with python and docker required"

        overlap, missing = self.matcher._calculate_skill_overlap(cv_skills, job_desc)

        assert len(overlap) == 2


class TestBatchEmbeddings:
    """Test batch embeddings functionality"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    @patch('agents.matcher.SmartMatcher._create_embeddings_batch')
    def test_batch_embeddings_called_once(self, mock_batch):
        """Test that batch embeddings is called once for all jobs"""
        # Setup mock return value
        mock_batch.return_value = [
            [0.1, 0.2, 0.3],  # Job 1 embedding
            [0.4, 0.5, 0.6],  # Job 2 embedding
            [0.7, 0.8, 0.9]   # Job 3 embedding
        ]

        texts = ["Job 1 description", "Job 2 description", "Job 3 description"]
        embeddings = self.matcher._create_embeddings_batch(texts)

        # Should be called once
        mock_batch.assert_called_once()
        assert len(embeddings) == 3

    def test_batch_embeddings_returns_correct_count(self):
        """Test that batch returns same number of embeddings as inputs"""
        with patch.object(self.matcher.client.embeddings, 'create') as mock_create:
            # Mock OpenAI response
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1, 0.2]),
                MagicMock(embedding=[0.3, 0.4]),
                MagicMock(embedding=[0.5, 0.6])
            ]
            mock_create.return_value = mock_response

            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = self.matcher._create_embeddings_batch(texts)

            assert len(embeddings) == 3
            assert len(embeddings[0]) == 2
            assert embeddings[0] == [0.1, 0.2]
            assert embeddings[1] == [0.3, 0.4]
            assert embeddings[2] == [0.5, 0.6]

    def test_batch_embeddings_cleans_text(self):
        """Test that batch embeddings cleans text properly"""
        with patch.object(self.matcher.client.embeddings, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2])]
            mock_create.return_value = mock_response

            # Text with extra whitespace
            texts = ["Text   with    lots    of    spaces"]
            self.matcher._create_embeddings_batch(texts)

            # Check that the text was cleaned before being sent
            called_with = mock_create.call_args[1]['input']
            assert "   " not in called_with[0]  # No triple spaces

    def test_batch_embeddings_truncates_long_text(self):
        """Test that batch embeddings truncates very long text"""
        with patch.object(self.matcher.client.embeddings, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2])]
            mock_create.return_value = mock_response

            # Create text longer than 8000 chars
            long_text = "x" * 10000
            texts = [long_text]
            self.matcher._create_embeddings_batch(texts)

            # Check that text was truncated
            called_with = mock_create.call_args[1]['input']
            assert len(called_with[0]) <= 8000

    def test_batch_embeddings_efficiency(self):
        """Test that batch is more efficient than individual calls"""
        with patch.object(self.matcher.client.embeddings, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1, 0.2]),
                MagicMock(embedding=[0.3, 0.4]),
                MagicMock(embedding=[0.5, 0.6]),
                MagicMock(embedding=[0.7, 0.8]),
                MagicMock(embedding=[0.9, 1.0])
            ]
            mock_create.return_value = mock_response

            # Batch processing 5 texts
            texts = [f"Text {i}" for i in range(5)]
            self.matcher._create_embeddings_batch(texts)

            # Should be called only ONCE for all 5 texts!
            assert mock_create.call_count == 1


class TestBaseScore:
    """Test base score calculation"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    def test_perfect_match(self):
        """Test scoring with perfect similarity and skill overlap"""
        # Create identical embeddings (similarity = 1.0)
        cv_embedding = [1.0, 2.0, 3.0, 4.0, 5.0]
        job_embedding = [1.0, 2.0, 3.0, 4.0, 5.0]

        cv_skills = ["Python", "Docker"]
        job_desc = "Python and Docker expert needed"

        score = self.matcher._calculate_base_score(
            cv_embedding, job_embedding, cv_skills, job_desc
        )

        # Should be high (close to 100)
        assert score > 80

    def test_low_similarity(self):
        """Test scoring with low similarity"""
        # Create very different embeddings
        cv_embedding = [1.0, 0.0, 0.0]
        job_embedding = [0.0, 1.0, 0.0]

        cv_skills = ["Python"]
        job_desc = "Python developer"

        score = self.matcher._calculate_base_score(
            cv_embedding, job_embedding, cv_skills, job_desc
        )

        # Should be low
        assert score < 50

    def test_score_range(self):
        """Test that score is always between 0-100"""
        cv_embedding = [1.0, 2.0, 3.0]
        job_embedding = [-1.0, -2.0, -3.0]

        cv_skills = ["Python"]
        job_desc = "Java developer"

        score = self.matcher._calculate_base_score(
            cv_embedding, job_embedding, cv_skills, job_desc
        )

        assert 0 <= score <= 100


class TestInsightsBonus:
    """Test company insights bonus/penalty"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    def test_positive_sentiment_bonus(self):
        """Test that positive sentiment adds bonus"""
        base_score = 50.0
        insights = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="positive"
        )

        adjusted_score = self.matcher._apply_insights_bonus(base_score, insights)

        assert adjusted_score > base_score

    def test_negative_sentiment_penalty(self):
        """Test that negative sentiment reduces score"""
        base_score = 50.0
        insights = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="negative"
        )

        adjusted_score = self.matcher._apply_insights_bonus(base_score, insights)

        assert adjusted_score < base_score

    def test_neutral_sentiment_no_change(self):
        """Test that neutral sentiment doesn't change score much"""
        base_score = 50.0
        insights = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="neutral"
        )

        adjusted_score = self.matcher._apply_insights_bonus(base_score, insights)

        # Should be same or very close
        assert abs(adjusted_score - base_score) < 1

    def test_score_stays_in_bounds(self):
        """Test that adjusted score stays within 0-100"""
        # Test with very high base score
        insights_positive = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="positive"
        )

        score = self.matcher._apply_insights_bonus(98.0, insights_positive)
        assert score <= 100

        # Test with very low base score
        insights_negative = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="negative"
        )

        score = self.matcher._apply_insights_bonus(5.0, insights_negative)
        assert score >= 0


class TestRecommendation:
    """Test recommendation generation"""

    def setup_method(self):
        """Initialize matcher for each test"""
        self.matcher = SmartMatcher()

    def test_strong_match(self):
        """Test that high scores get 'Strong Match'"""
        recommendation = self.matcher._generate_recommendation(85.0)
        assert recommendation == "Strong Match"

    def test_good_fit(self):
        """Test scores 65-79 get 'Good Fit'"""
        recommendation = self.matcher._generate_recommendation(70.0)
        assert recommendation == "Good Fit"

    def test_consider(self):
        """Test scores 50-64 get 'Consider'"""
        recommendation = self.matcher._generate_recommendation(55.0)
        assert recommendation == "Consider"

    def test_skip(self):
        """Test low scores get 'Skip'"""
        recommendation = self.matcher._generate_recommendation(30.0)
        assert recommendation == "Skip"


class TestFullMatching:
    """Integration tests for full matching pipeline"""

    @pytest.mark.asyncio
    async def test_match_and_rank(self):
        """Test the full match_and_rank pipeline"""
        matcher = SmartMatcher()

        # Create sample CV
        cv = CVAnalysis(
            skills=["Python", "Docker", "PostgreSQL"],
            experience_level="Mid",
            years_of_experience=3,
            preferred_locations=["Tel Aviv"],
            key_achievements=["Built microservices"]
        )

        # Create sample jobs
        jobs = [
            Job(
                title="Python Developer",
                company="TechCorp",
                location="Tel Aviv",
                description="Looking for Python developer with Docker and PostgreSQL",
                url="https://example.com/job1"
            ),
            Job(
                title="Java Developer",
                company="JavaCorp",
                location="Tel Aviv",
                description="Java and Spring Boot expert needed",
                url="https://example.com/job2"
            )
        ]

        # Create company insights
        insights = [
            CompanyInsights(company_name="TechCorp", reddit_sentiment="positive"),
            CompanyInsights(company_name="JavaCorp", reddit_sentiment="neutral")
        ]

        # Run matching
        matches = await matcher.match_and_rank(cv, jobs, insights)

        # Verify results
        assert len(matches) == 2
        assert isinstance(matches[0], JobMatch)

        # First match should be TechCorp (better skill match)
        assert matches[0].job.company == "TechCorp"
        assert matches[0].match_score > matches[1].match_score

        # Verify all matches have required fields
        for match in matches:
            assert match.job is not None
            assert match.company_insights is not None
            assert 0 <= match.match_score <= 100
            assert match.recommendation in ["Strong Match", "Good Fit", "Consider", "Skip"]
            assert len(match.reasoning) > 0

    @pytest.mark.asyncio
    async def test_empty_jobs_list(self):
        """Test behavior with empty jobs list"""
        matcher = SmartMatcher()

        cv = CVAnalysis(
            skills=["Python"],
            experience_level="Junior",
            years_of_experience=1
        )

        matches = await matcher.match_and_rank(cv, [], [])

        assert matches == []

    @pytest.mark.asyncio
    async def test_matches_are_sorted(self):
        """Test that matches are sorted by score (highest first)"""
        matcher = SmartMatcher()

        cv = CVAnalysis(
            skills=["Python", "JavaScript", "React"],
            experience_level="Senior",
            years_of_experience=5
        )

        jobs = [
            Job(
                title="Junior Java Developer",
                company="CompanyA",
                location="Remote",
                description="Java and Spring Boot",
                url="https://example.com/job1"
            ),
            Job(
                title="Senior Python Developer",
                company="CompanyB",
                location="Remote",
                description="Python, JavaScript, React expert needed",
                url="https://example.com/job2"
            ),
            Job(
                title="DevOps Engineer",
                company="CompanyC",
                location="Remote",
                description="Kubernetes and Terraform",
                url="https://example.com/job3"
            )
        ]

        insights = [
            CompanyInsights(company_name="CompanyA", reddit_sentiment="neutral"),
            CompanyInsights(company_name="CompanyB", reddit_sentiment="positive"),
            CompanyInsights(company_name="CompanyC", reddit_sentiment="neutral")
        ]

        matches = await matcher.match_and_rank(cv, jobs, insights)

        # Verify sorted by score
        for i in range(len(matches) - 1):
            assert matches[i].match_score >= matches[i + 1].match_score


# Run tests with: pytest tests/test_matcher.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
