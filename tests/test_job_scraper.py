"""
Unit tests for Job Scraper Agent
Tests query expansion, API search, and job deduplication
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from typing import List

from agents.job_scraper import JobScraper
from models.models import Job


class TestJobScraperInitialization:
    """Test JobScraper initialization with different configurations"""

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key",
        "JSEARCH_API_KEY": "test_jsearch_key",
        "BRAVE_SEARCH_API_KEY": "test_brave_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def test_init_with_all_credentials(self, mock_brave, mock_openai):
        """Test successful initialization with all API keys"""
        scraper = JobScraper()

        assert scraper.openai_client is not None
        assert scraper.use_jsearch is True
        assert scraper.use_brave_search is True

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_openai_key_raises_error(self):
        """Test that missing OpenAI API key raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            JobScraper()
        assert "OPENAI_API_KEY not found" in str(excinfo.value)

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key"
        # No JSEARCH_API_KEY
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def test_init_without_jsearch_disables_jsearch(self, mock_brave, mock_openai):
        """Test initialization without JSearch disables JSearch"""
        scraper = JobScraper()

        assert scraper.use_jsearch is False
        assert scraper.use_brave_search is True

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key",
        "JSEARCH_API_KEY": "test_jsearch_key"
        # No BRAVE_SEARCH_API_KEY
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent', side_effect=ValueError("No Brave key"))
    def test_init_without_brave_disables_brave(self, mock_brave, mock_openai):
        """Test initialization without Brave Search disables Brave"""
        scraper = JobScraper()

        assert scraper.use_jsearch is True
        assert scraper.use_brave_search is False


class TestQueryExpansion:
    """Test smart query expansion using OpenAI"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key",
        "JSEARCH_API_KEY": "test_jsearch_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave, mock_openai_cls):
        """Create test scraper"""
        mock_openai_instance = MagicMock()
        mock_openai_cls.return_value = mock_openai_instance

        scraper = JobScraper(use_brave_search=False)
        scraper.openai_client = mock_openai_instance
        return scraper

    def test_expand_job_query_success(self, scraper):
        """Test successful query expansion"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["AI Intern", "Junior AI Engineer", "Machine Learning Intern"]'

        scraper.openai_client.chat.completions.create.return_value = mock_response

        # Test expansion
        result = scraper._expand_job_query("ai student")

        assert len(result) == 3
        assert "AI Intern" in result
        assert "Junior AI Engineer" in result
        assert "Machine Learning Intern" in result

    def test_expand_job_query_with_python_dev(self, scraper):
        """Test expansion for Python developer query"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["Python Developer", "Backend Python Engineer", "Python Software Engineer", "Junior Python Developer"]'

        scraper.openai_client.chat.completions.create.return_value = mock_response

        result = scraper._expand_job_query("python dev")

        assert len(result) == 4
        assert any("Python" in title for title in result)

    def test_expand_job_query_fallback_on_error(self, scraper):
        """Test fallback to original query when OpenAI fails"""
        scraper.openai_client.chat.completions.create.side_effect = Exception("API Error")

        result = scraper._expand_job_query("software engineer")

        assert len(result) == 1
        assert result[0] == "software engineer"

    def test_expand_job_query_invalid_json_fallback(self, scraper):
        """Test fallback when OpenAI returns invalid JSON"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'This is not valid JSON'

        scraper.openai_client.chat.completions.create.return_value = mock_response

        result = scraper._expand_job_query("data scientist")

        assert len(result) == 1
        assert result[0] == "data scientist"


class TestMockJobs:
    """Test mock job generation"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave, mock_openai):
        """Create test scraper"""
        return JobScraper(use_brave_search=False)

    def test_get_mock_jobs_returns_jobs(self, scraper):
        """Test that mock jobs are generated correctly"""
        jobs = scraper._get_mock_jobs("Python Developer", num_jobs=3)

        assert len(jobs) > 0
        assert len(jobs) <= 3
        assert all(isinstance(job, Job) for job in jobs)

    def test_get_mock_jobs_with_location_filter(self, scraper):
        """Test location filtering in mock jobs"""
        jobs = scraper._get_mock_jobs("Python Developer", location="Tel Aviv", num_jobs=10)

        assert all(isinstance(job, Job) for job in jobs)
        # All jobs should contain Tel Aviv or Remote
        for job in jobs:
            assert "Tel Aviv" in job.location or "Remote" in job.location

    def test_get_mock_jobs_structure(self, scraper):
        """Test that mock jobs have correct structure"""
        jobs = scraper._get_mock_jobs("Software Engineer", num_jobs=1)

        assert len(jobs) == 1
        job = jobs[0]

        assert hasattr(job, 'title')
        assert hasattr(job, 'company')
        assert hasattr(job, 'location')
        assert hasattr(job, 'description')
        assert hasattr(job, 'url')
        assert hasattr(job, 'posted_date')
        assert hasattr(job, 'source')

        assert isinstance(job.title, str)
        assert isinstance(job.company, str)
        assert isinstance(job.location, str)
        assert isinstance(job.description, str)


class TestJSearchAPI:
    """Test JSearch API integration"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key",
        "JSEARCH_API_KEY": "test_jsearch_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave, mock_openai):
        """Create test scraper with JSearch enabled"""
        return JobScraper(use_brave_search=False)

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_search_jsearch_api_success(self, mock_get, scraper):
        """Test successful JSearch API call"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "job_title": "Software Engineer",
                    "employer_name": "Tech Company",
                    "job_city": "Tel Aviv",
                    "job_country": "Israel",
                    "job_description": "Great opportunity",
                    "job_apply_link": "https://example.com/job1",
                    "job_posted_at_datetime_utc": "2025-10-20",
                    "job_is_remote": False
                }
            ]
        }
        mock_get.return_value = mock_response

        jobs = await scraper._search_jsearch_api("Software Engineer", location="Tel Aviv", num_jobs=5)

        assert len(jobs) == 1
        assert jobs[0].title == "Software Engineer"
        assert jobs[0].company == "Tech Company"
        assert jobs[0].location == "Tel Aviv, Israel"
        assert jobs[0].source == "jsearch"

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_search_jsearch_api_no_results(self, mock_get, scraper):
        """Test JSearch API with no results"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        jobs = await scraper._search_jsearch_api("Nonexistent Job", location="Mars", num_jobs=5)

        assert len(jobs) == 0

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_search_jsearch_api_error(self, mock_get, scraper):
        """Test JSearch API error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            await scraper._search_jsearch_api("Software Engineer", num_jobs=5)

        assert "JSearch API error" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_search_jsearch_remote_fallback(self, mock_get, scraper):
        """Test fallback to remote search when location search fails"""
        # First call (with location) returns no results
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {"data": []}

        # Second call (remote) returns results
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "data": [
                {
                    "job_title": "Remote Developer",
                    "employer_name": "Remote Co",
                    "job_city": None,
                    "job_country": None,
                    "job_description": "Remote work",
                    "job_apply_link": "https://example.com/remote1",
                    "job_is_remote": True
                }
            ]
        }

        mock_get.side_effect = [mock_response_1, mock_response_2]

        jobs = await scraper._search_jsearch_api("Developer", location="Obscure City", num_jobs=5)

        assert len(jobs) == 1
        assert jobs[0].location == "Remote"


class TestConvertToJobs:
    """Test conversion of API responses to Job objects"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave, mock_openai):
        """Create test scraper"""
        return JobScraper(use_brave_search=False)

    def test_convert_to_jobs_with_full_data(self, scraper):
        """Test conversion with complete job data"""
        jobs_data = [
            {
                "job_title": "Python Developer",
                "employer_name": "Tech Corp",
                "job_city": "Tel Aviv",
                "job_country": "Israel",
                "job_state": None,
                "job_description": "Python development role",
                "job_apply_link": "https://example.com/job1",
                "job_posted_at_datetime_utc": "2025-10-20",
                "job_is_remote": False
            }
        ]

        jobs = scraper._convert_to_jobs(jobs_data, num_jobs=5)

        assert len(jobs) == 1
        assert jobs[0].title == "Python Developer"
        assert jobs[0].company == "Tech Corp"
        assert jobs[0].location == "Tel Aviv, Israel"

    def test_convert_to_jobs_remote_position(self, scraper):
        """Test conversion of remote job"""
        jobs_data = [
            {
                "job_title": "Remote Engineer",
                "employer_name": "Remote Inc",
                "job_city": None,
                "job_country": None,
                "job_state": None,
                "job_description": "Remote work",
                "job_apply_link": "https://example.com/remote",
                "job_is_remote": True
            }
        ]

        jobs = scraper._convert_to_jobs(jobs_data, num_jobs=5)

        assert len(jobs) == 1
        assert jobs[0].location == "Remote"

    def test_convert_to_jobs_respects_limit(self, scraper):
        """Test that conversion respects num_jobs limit"""
        jobs_data = [{"job_title": f"Job {i}", "employer_name": "Company", "job_description": "Desc"} for i in range(10)]

        jobs = scraper._convert_to_jobs(jobs_data, num_jobs=3)

        assert len(jobs) == 3


class TestMainSearchMethod:
    """Test the main search method with query expansion and multi-source"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key",
        "JSEARCH_API_KEY": "test_jsearch_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave_cls, mock_openai_cls):
        """Create test scraper with mocked APIs"""
        mock_openai_instance = MagicMock()
        mock_openai_cls.return_value = mock_openai_instance

        mock_brave_instance = MagicMock()
        mock_brave_cls.return_value = mock_brave_instance

        scraper = JobScraper()
        scraper.openai_client = mock_openai_instance
        scraper.brave_agent = mock_brave_instance
        return scraper

    @pytest.mark.asyncio
    async def test_search_full_workflow(self, scraper):
        """Test complete search workflow with query expansion"""
        # Mock query expansion
        scraper._expand_job_query = Mock(return_value=["Python Developer", "Python Engineer"])

        # Mock JSearch results
        jsearch_jobs = [
            Job(title="Python Dev 1", company="Company A", location="Tel Aviv",
                description="Job 1", url="https://example.com/1", source="jsearch"),
            Job(title="Python Dev 2", company="Company B", location="Tel Aviv",
                description="Job 2", url="https://example.com/2", source="jsearch")
        ]
        scraper._search_jsearch_api = AsyncMock(return_value=jsearch_jobs)

        # Mock Brave Search results
        brave_jobs = [
            Job(title="Python Engineer 1", company="Company C", location="Tel Aviv",
                description="Job 3", url="https://example.com/3", source="brave_search"),
            Job(title="Python Engineer 2", company="Company D", location="Tel Aviv",
                description="Job 4", url="https://example.com/4", source="brave_search")
        ]
        scraper.brave_agent.search_jobs = AsyncMock(return_value=brave_jobs)

        # Execute search
        results = await scraper.search("python dev", location="Tel Aviv", num_jobs=10)

        # Verify query expansion was called
        scraper._expand_job_query.assert_called_once_with("python dev")

        # Verify results
        assert len(results) > 0
        assert all(isinstance(job, Job) for job in results)

    @pytest.mark.asyncio
    async def test_search_deduplication(self, scraper):
        """Test that duplicate jobs are removed"""
        scraper._expand_job_query = Mock(return_value=["Developer"])

        # Create duplicate jobs
        duplicate_jobs = [
            Job(title="Python Developer", company="Tech Corp", location="Tel Aviv",
                description="Job", url="https://example.com/1", source="jsearch"),
            Job(title="Python Developer", company="Tech Corp", location="Tel Aviv",
                description="Job", url="https://example.com/1", source="jsearch"),  # Duplicate URL
        ]
        scraper._search_jsearch_api = AsyncMock(return_value=duplicate_jobs)
        scraper.use_brave_search = False

        results = await scraper.search("developer", num_jobs=10)

        # Should have only 1 job (duplicate removed)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_with_no_sources(self, scraper):
        """Test search when no sources are available"""
        scraper.use_jsearch = False
        scraper.use_brave_search = False
        scraper._expand_job_query = Mock(return_value=["Developer"])

        results = await scraper.search("developer", num_jobs=10)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_balances_sources(self, scraper):
        """Test that search balances results from different sources"""
        scraper._expand_job_query = Mock(return_value=["Developer"])

        # Mock 10 JSearch jobs
        jsearch_jobs = [
            Job(title=f"Job {i}", company=f"Company {i}", location="Tel Aviv",
                description="Desc", url=f"https://example.com/j{i}", source="jsearch")
            for i in range(10)
        ]
        scraper._search_jsearch_api = AsyncMock(return_value=jsearch_jobs)

        # Mock 10 Brave jobs
        brave_jobs = [
            Job(title=f"Brave Job {i}", company=f"Brave Co {i}", location="Tel Aviv",
                description="Desc", url=f"https://example.com/b{i}", source="brave_search")
            for i in range(10)
        ]
        scraper.brave_agent.search_jobs = AsyncMock(return_value=brave_jobs)

        results = await scraper.search("developer", num_jobs=10)

        # Count sources
        jsearch_count = sum(1 for job in results if job.source == "jsearch")
        brave_count = sum(1 for job in results if job.source == "brave_search")

        # Should be roughly balanced (50/50 split)
        assert jsearch_count > 0
        assert brave_count > 0
        assert abs(jsearch_count - brave_count) <= 2  # Allow small difference

    @pytest.mark.asyncio
    async def test_search_handles_api_failures_gracefully(self, scraper):
        """Test that search continues even if one source fails"""
        scraper._expand_job_query = Mock(return_value=["Developer"])

        # JSearch fails
        scraper._search_jsearch_api = AsyncMock(side_effect=Exception("API Error"))

        # Brave succeeds
        brave_jobs = [
            Job(title="Brave Job", company="Company", location="Tel Aviv",
                description="Desc", url="https://example.com/1", source="brave_search")
        ]
        scraper.brave_agent.search_jobs = AsyncMock(return_value=brave_jobs)

        results = await scraper.search("developer", num_jobs=10)

        # Should still return Brave results
        assert len(results) == 1
        assert results[0].source == "brave_search"


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai_key"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def scraper(self, mock_brave, mock_openai):
        """Create test scraper"""
        return JobScraper(use_brave_search=False)

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, scraper):
        """Test search with empty query string"""
        scraper._expand_job_query = Mock(return_value=[""])
        scraper._search_jsearch_api = AsyncMock(return_value=[])

        results = await scraper.search("", num_jobs=10)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_special_characters(self, scraper):
        """Test search with special characters in query"""
        scraper._expand_job_query = Mock(return_value=["C++ Developer"])
        scraper._search_jsearch_api = AsyncMock(return_value=[])

        results = await scraper.search("C++ Dev @#$%", num_jobs=10)

        assert isinstance(results, list)

    def test_get_mock_jobs_with_zero_jobs(self, scraper):
        """Test mock jobs with num_jobs=0"""
        jobs = scraper._get_mock_jobs("Developer", num_jobs=0)

        assert len(jobs) == 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])