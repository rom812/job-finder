"""
Agent 4: Smart Matcher
Matches CV to jobs using embeddings and intelligent scoring
"""

import os
from typing import List, Tuple
from dotenv import load_dotenv
from openai import OpenAI

from models.models import CVAnalysis, Job, CompanyInsights, JobMatch

# Load environment variables
load_dotenv()


class SmartMatcher:
    """
    Agent 4: Smart Matcher

    Matches a CV to jobs using:
    - OpenAI embeddings (semantic similarity)
    - Skill overlap analysis
    - Company insights sentiment

    Returns ranked JobMatch objects with scores and reasoning.
    """

    def __init__(self):
        """Initialize the Smart Matcher with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-small"  # Fast and cheap!

    def _create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding vector for text using OpenAI

        Args:
            text: Text to embed (CV or job description)

        Returns:
            List of floats (vector of 1536 dimensions)

        Example:
            embedding = self._create_embedding("Python developer with 3 years experience")
            # Returns: [0.23, -0.45, 0.67, ...] (1536 numbers)
        """
        # Clean text - remove extra whitespace
        text = " ".join(text.split())

        # Limit text length (embeddings have max tokens)
        if len(text) > 8000:
            text = text[:8000]

        # Call OpenAI embeddings API
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )

        # Extract the embedding vector
        embedding = response.data[0].embedding

        return embedding

    def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts in a single API call (BATCH)

        This is 10x more efficient than calling _create_embedding() in a loop!

        Args:
            texts: List of texts to embed (e.g., multiple job descriptions)

        Returns:
            List of embedding vectors (one per text)

        Example:
            texts = ["Job 1 description", "Job 2 description", "Job 3 description"]
            embeddings = self._create_embeddings_batch(texts)
            # Returns: [[0.23, -0.45, ...], [0.12, 0.34, ...], [0.56, -0.78, ...]]
            # One API call instead of 3!
        """
        # Clean all texts
        cleaned_texts = []
        for text in texts:
            # Remove extra whitespace
            text = " ".join(text.split())
            # Limit text length (embeddings have max tokens)
            if len(text) > 8000:
                text = text[:8000]
            cleaned_texts.append(text)

        # Call OpenAI embeddings API with batch
        # This is the magic - one API call for ALL texts!
        response = self.client.embeddings.create(
            input=cleaned_texts,  # Pass list instead of single string
            model=self.embedding_model
        )

        # Extract all embedding vectors
        # response.data is a list of embedding objects
        embeddings = [item.embedding for item in response.data]

        return embeddings

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Cosine similarity measures how similar two vectors are.
        Result: 0 = completely different, 1 = identical

        Args:
            vec1: First vector (e.g., CV embedding)
            vec2: Second vector (e.g., job embedding)

        Returns:
            Similarity score between 0 and 1

        Formula:
            similarity = (A · B) / (||A|| × ||B||)
            Where · is dot product, ||A|| is magnitude
        """
        # Implement cosine similarity using numpy:
        import numpy as np

        # Convert to numpy arrays
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        # 1. Calculate dot product
        dot_product = np.dot(vec1, vec2)

        # 2. Calculate magnitude of vec1
        magnitude1 = np.linalg.norm(vec1)

        # 3. Calculate magnitude of vec2
        magnitude2 = np.linalg.norm(vec2)

        # 4. Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        # 5. Calculate and return cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)

        return float(similarity)

    def _calculate_skill_overlap(
        self,
        cv_skills: List[str],
        job_description: str
    ) -> Tuple[List[str], List[str]]:
        """
        Calculate which skills from CV match the job, and which are missing

        Args:
            cv_skills: List of skills from CV (e.g., ["Python", "Docker", "AWS"])
            job_description: Full job description text

        Returns:
            Tuple of (overlapping_skills, missing_skills)
            - overlapping_skills: Skills from CV that appear in job description
            - missing_skills: Skills mentioned in job but not in CV

        Example:
            CV skills: ["Python", "Docker"]
            Job description: "Looking for Python and Kubernetes expert"

            Returns:
                (["Python"], ["Kubernetes"])
        """
        import re
        job_desc_lower = job_description.lower()

        # Find overlapping skills (skills from CV that are in job description)
        # Use word boundaries to avoid false matches (e.g., "Java" in "JavaScript")
        overlapping = []
        for skill in cv_skills:
            # Check if skill appears as a whole word in job description
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, job_desc_lower):
                overlapping.append(skill)

        # Common skills to check for in job description (that might be missing from CV)
        common_tech_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "React", "Vue", "Angular", "Node.js",
            "PostgreSQL", "MongoDB", "Redis",
            "Kafka", "RabbitMQ", "GraphQL", "REST",
            "CI/CD", "Jenkins", "GitLab", "GitHub Actions",
            "Terraform", "Ansible", "Linux"
        ]

        # Find skills mentioned in job but missing from CV
        missing = [
            skill for skill in common_tech_skills
            if skill.lower() in job_desc_lower and skill not in cv_skills
        ]

        return overlapping, missing

    def _calculate_base_score(
        self,
        cv_embedding: List[float],
        job_embedding: List[float],
        cv_skills: List[str],
        job_description: str
    ) -> float:
        """
        Calculate base match score (0-100) using embeddings and skill overlap

        Args:
            cv_embedding: CV embedding vector
            job_embedding: Job embedding vector
            cv_skills: Skills from CV
            job_description: Job description text

        Returns:
            Base score between 0-100
        """
        # Calculate semantic similarity (0-1)
        similarity = self._cosine_similarity(cv_embedding, job_embedding)

        # Calculate skill overlap
        overlapping, missing = self._calculate_skill_overlap(cv_skills, job_description)

        # NEW SCORING SYSTEM - More weight to skills!
        # Base score from similarity (0-50 points) - REDUCED from 70
        score = similarity * 50

        # Skill overlap - TWO components:
        # 1. Absolute overlap bonus (0-30 points) - INCREASED from 20
        if overlapping:
            # Give points based on absolute number of overlapping skills
            # More overlapping skills = higher score
            overlap_bonus = min(len(overlapping) * 4, 30)  # 4 points per skill, max 30
            score += overlap_bonus

        # 2. Skill coverage ratio (0-20 points)
        # What percentage of YOUR skills are used in this job?
        if cv_skills:
            skill_match_ratio = len(overlapping) / len(cv_skills)
            score += skill_match_ratio * 20

        # Reduced penalty for missing skills (0-5 points) - REDUCED from 10
        # It's OK to be missing some skills if you have strong overlap!
        if missing:
            penalty = min(len(missing) * 1, 5)
            score -= penalty

        # Ensure score is between 0-100
        return max(0, min(100, score))

    def _apply_insights_bonus(
        self,
        base_score: float,
        company_insights: CompanyInsights
    ) -> float:
        """
        Apply bonus/penalty based on company insights

        Args:
            base_score: Base match score (0-100)
            company_insights: Company insights from Agent 3

        Returns:
            Adjusted score (0-100)
        """
        score = base_score

        # Sentiment bonus/penalty
        if company_insights.reddit_sentiment == "positive":
            score += 5  # Bonus for positive company culture
        elif company_insights.reddit_sentiment == "negative":
            score -= 10  # Penalty for negative reviews

        # Ensure score stays within 0-100
        return max(0, min(100, score))

    def _generate_recommendation(self, score: float) -> str:
        """
        Generate recommendation based on score

        Args:
            score: Match score (0-100)

        Returns:
            Recommendation string: "Strong Match", "Good Fit", "Consider", or "Skip"
        """
        if score >= 80:
            return "Strong Match"
        elif score >= 65:
            return "Good Fit"
        elif score >= 50:
            return "Consider"
        else:
            return "Skip"

    def _generate_reasoning(
        self,
        score: float,
        skill_overlap: List[str],
        skill_gaps: List[str],
        company_insights: CompanyInsights
    ) -> List[str]:
        """
        Generate human-readable reasoning for the match score

        Args:
            score: Match score
            skill_overlap: Skills that match
            skill_gaps: Skills that are missing
            company_insights: Company insights

        Returns:
            List of reasoning strings
        """
        reasoning = []

        # Score-based reasoning
        if score >= 80:
            reasoning.append(f"Excellent match with {score:.0f}% compatibility")
        elif score >= 65:
            reasoning.append(f"Good fit with {score:.0f}% compatibility")
        else:
            reasoning.append(f"Moderate fit with {score:.0f}% compatibility")

        # Skill overlap reasoning
        if skill_overlap:
            reasoning.append(f"Strong skill alignment: {', '.join(skill_overlap[:5])}")

        # Skill gaps reasoning
        if skill_gaps:
            reasoning.append(f"Missing skills: {', '.join(skill_gaps[:3])}")

        # Company insights reasoning
        if company_insights.reddit_sentiment == "positive":
            reasoning.append("Company has positive reviews and culture")
        elif company_insights.reddit_sentiment == "negative":
            reasoning.append("⚠️  Company has some negative reviews")

        return reasoning

    async def match_and_rank(
        self,
        cv_analysis: CVAnalysis,
        jobs: List[Job],
        company_insights_list: List[CompanyInsights],
        desired_role: str = "",
        desired_location: str = ""
    ) -> List[JobMatch]:
        """
        Main method: Match CV to jobs and return ranked results

        Args:
            cv_analysis: Analyzed CV from Agent 1
            jobs: List of jobs from Agent 2
            company_insights_list: List of company insights from Agent 3
            desired_role: User's desired job role (e.g., "Python Developer")
            desired_location: User's preferred location (e.g., "United States", "Remote")

        Returns:
            List of JobMatch objects, sorted by score (highest first)

        Example:
            matcher = SmartMatcher()
            matches = await matcher.match_and_rank(cv, jobs, insights)

            for match in matches[:5]:  # Top 5
                print(f"{match.job.title}: {match.match_score}/100")
        """
        print(f"🎯 Matching CV to {len(jobs)} jobs...")

        # Step 1: Create RICH CV embedding (including context and user preferences)
        print(f"   📊 Creating rich CV embedding...")

        # Build a rich, contextual CV description for better embedding
        # Include skills multiple times with context to increase their weight
        skills_context = []
        for skill in cv_analysis.skills:
            # Repeat each skill 2-3 times with context to boost its importance
            skills_context.append(f"Expert in {skill}")
            skills_context.append(f"Professional {skill} experience")
            if cv_analysis.years_of_experience >= 3:
                skills_context.append(f"Advanced {skill} skills")

        # Build comprehensive CV text
        cv_text = f"""
        Professional {desired_role or 'Developer'} with {cv_analysis.years_of_experience} years of experience.
        {cv_analysis.experience_level} level professional.

        Core Technical Skills:
        {' '.join(skills_context)}

        Technical Expertise: {', '.join(cv_analysis.skills)}

        Key Achievements and Experience:
        {' '.join(cv_analysis.key_achievements)}

        Career Level: {cv_analysis.experience_level} developer with proven track record
        Years of Experience: {cv_analysis.years_of_experience} years

        Looking for: {desired_role or 'challenging opportunities'}
        Preferred Location: {desired_location or 'flexible'}
        Location Preferences: {', '.join(cv_analysis.preferred_locations)}

        This candidate has strong capabilities in: {', '.join(cv_analysis.skills)}
        """

        cv_embedding = self._create_embedding(cv_text)
        print(f"   ✅ Rich CV embedding created ({len(cv_embedding)} dimensions with skill emphasis)")

        # Step 2: Create embeddings for ALL jobs in ONE API call (BATCH!)
        matches = []

        # Handle empty jobs list
        if not jobs:
            print(f"   ⚠️  No jobs to match!")
            return matches

        print(f"   🚀 Creating embeddings for {len(jobs)} jobs (batch mode - 10x faster)...")
        job_texts = [f"{job.title} {job.description}" for job in jobs]
        job_embeddings = self._create_embeddings_batch(job_texts)
        print(f"   ✅ All job embeddings created in one API call!")

        # Step 3: Match each job with its embedding

        for i, (job, job_embedding) in enumerate(zip(jobs, job_embeddings)):
            print(f"   🔍 Matching job {i+1}/{len(jobs)}: {job.title} at {job.company}")

            # Calculate skill overlap and gaps
            skill_overlap, skill_gaps = self._calculate_skill_overlap(
                cv_analysis.skills,
                job.description
            )

            # Calculate base score
            base_score = self._calculate_base_score(
                cv_embedding,
                job_embedding,
                cv_analysis.skills,
                job.description
            )

            # Find matching company insights
            company_insights = next(
                (ci for ci in company_insights_list if ci.company_name == job.company),
                CompanyInsights(company_name=job.company, reddit_sentiment="neutral")
            )

            # Apply company insights bonus
            final_score = self._apply_insights_bonus(base_score, company_insights)

            # Generate recommendation
            recommendation = self._generate_recommendation(final_score)

            # Generate reasoning
            reasoning = self._generate_reasoning(
                final_score,
                skill_overlap,
                skill_gaps,
                company_insights
            )

            # Create JobMatch object
            match = JobMatch(
                job=job,
                company_insights=company_insights,
                match_score=final_score,
                skill_overlap=skill_overlap,
                skill_gaps=skill_gaps,
                recommendation=recommendation,
                reasoning=reasoning
            )

            matches.append(match)

        # Step 3: Sort by score (highest first)
        matches.sort(key=lambda m: m.match_score, reverse=True)

        if matches:
            print(f"\n✅ Matching complete! Top score: {matches[0].match_score:.1f}/100")
        else:
            print(f"\n✅ Matching complete! No jobs to match.")

        return matches


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio
    from agents.cv_analyzer import CVAnalyzer
    from agents.job_scraper import JobScraper
    from agents.news_agent import NewsAgent

    async def test():
        print("🧪 Testing Smart Matcher Agent\n")
        print("=" * 80)

        # Step 1: Analyze CV
        print("\n📄 Step 1: Analyzing CV...")
        cv_analyzer = CVAnalyzer()
        cv_analysis = await cv_analyzer.analyze("cvs/romCV.pdf")

        # Step 2: Get jobs
        print("\n🔍 Step 2: Fetching jobs...")
        job_scraper = JobScraper()
        jobs = await job_scraper.search("Python Developer", num_jobs=5)

        # Step 3: Get company insights
        print("\n🗞️  Step 3: Getting company insights...")
        news_agent = NewsAgent(use_mock=True)  # Use mock for speed
        insights = []
        for job in jobs:
            insight = await news_agent.get_insights(job.company)
            insights.append(insight)

        # Step 4: Match and rank!
        print("\n🎯 Step 4: Matching CV to jobs...")
        matcher = SmartMatcher()
        matches = await matcher.match_and_rank(cv_analysis, jobs, insights)

        # Display results
        print("\n" + "=" * 80)
        print("📊 MATCHING RESULTS (Top 5):")
        print("=" * 80)

        for i, match in enumerate(matches[:5], 1):
            print(f"\n{i}. {match.job.title} at {match.job.company}")
            print(f"   Score: {match.match_score:.1f}/100")
            print(f"   Recommendation: {match.recommendation}")
            print(f"   Skill Overlap: {', '.join(match.skill_overlap[:5]) if match.skill_overlap else 'None'}")
            print(f"   Skill Gaps: {', '.join(match.skill_gaps[:3]) if match.skill_gaps else 'None'}")
            print(f"   Reasoning:")
            for reason in match.reasoning:
                print(f"      • {reason}")
            print(f"   Company Sentiment: {match.company_insights.reddit_sentiment}")

        print("\n" + "=" * 80)
        print("✅ Smart Matcher Test Complete!")

    asyncio.run(test())
