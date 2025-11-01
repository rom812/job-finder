"""
Unit tests for Brave Search Agent
Tests all functionality including news search, job search, and API integration
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import asyncio
from typing import List

from agents.brave_search import BraveSearchAgent
from models.models import Job


class TestBraveSearchAgentInitialization:
    """Test BraveSearchAgent initialization"""

    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_api_key_12345"})
    def test_init_with_valid_api_key(self):
        """Test successful initialization with valid API key"""
        agent = BraveSearchAgent()
        assert agent.api_key == "test_api_key_12345"
        assert agent.base_url == "https://api.search.brave.com/res/v1/web/search"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            BraveSearchAgent()
        assert "BRAVE_SEARCH_API_KEY not found" in str(excinfo.value)

    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": ""})
    def test_init_with_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            BraveSearchAgent()
        assert "BRAVE_SEARCH_API_KEY not found" in str(excinfo.value)


class TestBuildJobQuery:
    """Test query building functionality"""

    @pytest.fixture(autouse=True)
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    def setup(self):
        """Setup test agent"""
        self.agent = BraveSearchAgent()
        yield

    def test_build_query_with_job_title_only(self):
        """Test query building with only job title"""
        query = self.agent._build_job_query("Python Developer")
        assert "Python Developer" in query
        assert "job OR jobs OR hiring OR career OR position" in query

    def test_build_query_with_location(self):
        """Test query building with job title and location"""
        query = self.agent._build_job_query("Python Developer", "Tel Aviv")
        assert "Python Developer" in query
        assert '"Tel Aviv"' in query
        assert "job OR jobs OR hiring OR career OR position" in query

    def test_build_query_with_special_characters(self):
        """Test query building with special characters in job title"""
        query = self.agent._build_job_query("C++ Developer", "New York")
        assert "C++ Developer" in query
        assert '"New York"' in query

    def test_build_query_with_remote_location(self):
        """Test query building with remote location"""
        query = self.agent._build_job_query("DevOps Engineer", "Remote")
        assert "DevOps Engineer" in query
        assert '"Remote"' in query


class TestExtractCompany:
    """Test company name extraction"""

    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    def setup_method(self):
        """Setup test agent"""
        self.agent = BraveSearchAgent()

    def test_extract_company_from_title_with_dash(self):
        """Test company extraction from title with dash separator"""
        result = {
            "title": "Software Engineer - Google",
            "url": "https://careers.google.com/jobs/123"
        }
        company = self.agent._extract_company(result)
        assert company == "Google"

    def test_extract_company_from_title_with_at(self):
        """Test company extraction from title with 'at' separator"""
        result = {
            "title": "Python Developer at Microsoft",
            "url": "https://careers.microsoft.com/jobs/456"
        }
        company = self.agent._extract_company(result)
        assert company == "Microsoft"

    def test_extract_company_from_linkedin_url(self):
        """Test company extraction from LinkedIn company URL"""
        result = {
            "title": "Backend Developer Position",
            "url": "https://www.linkedin.com/company/meta/jobs"
        }
        company = self.agent._extract_company(result)
        assert company == "Meta"

    def test_extract_company_from_domain(self):
        """Test company extraction from domain name"""
        result = {
            "title": "Senior Developer",
            "url": "https://www.apple.com/careers"
        }
        company = self.agent._extract_company(result)
        assert company == "Apple"

    def test_extract_company_fallback_unknown(self):
        """Test fallback to Unknown Company when extraction fails"""
        result = {
            "title": "Job Opening",
            "url": ""
        }
        company = self.agent._extract_company(result)
        assert company == "Unknown Company"

    def test_extract_company_with_multiple_dashes(self):
        """Test company extraction with multiple dashes in title"""
        result = {
            "title": "Senior DevOps - Remote - Amazon Web Services",
            "url": "https://aws.amazon.com/careers"
        }
        company = self.agent._extract_company(result)
        assert company == "Amazon Web Services"


class TestExtractLocation:
    """Test location extraction from text"""

    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    def setup_method(self):
        """Setup test agent"""
        self.agent = BraveSearchAgent()

    def test_extract_remote_location(self):
        """Test extraction of remote work location"""
        text = "We are hiring a Python developer for remote position"
        location = self.agent._extract_location(text)
        assert location == "Remote"

    def test_extract_tel_aviv(self):
        """Test extraction of Tel Aviv"""
        text = "Great opportunity in Tel Aviv city center"
        location = self.agent._extract_location(text)
        assert location == "Tel Aviv"

    def test_extract_jerusalem(self):
        """Test extraction of Jerusalem"""
        text = "Position available in Jerusalem area"
        location = self.agent._extract_location(text)
        assert location == "Jerusalem"

    def test_extract_hebrew_city(self):
        """Test extraction of Hebrew city name"""
        text = "משרה בתל אביב במרכז העיר"
        location = self.agent._extract_location(text)
        assert location == "תל אביב"

    def test_extract_work_from_home(self):
        """Test extraction of work from home"""
        text = "Work from home position available"
        location = self.agent._extract_location(text)
        assert location == "Remote"

    def test_extract_israel_general(self):
        """Test extraction of Israel as general location"""
        text = "Looking for developers in Israel"
        location = self.agent._extract_location(text)
        assert location == "Israel"

    def test_extract_no_location(self):
        """Test when no location is found"""
        text = "Great developer position with competitive salary"
        location = self.agent._extract_location(text)
        assert location is None

    def test_extract_herzliya(self):
        """Test extraction of Herzliya"""
        text = "Office located in Herzliya Pituach"
        location = self.agent._extract_location(text)
        assert location == "Herzliya"


class TestParseSearchResults:
    """Test parsing of search results into Job objects"""

    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    def setup_method(self):
        """Setup test agent"""
        self.agent = BraveSearchAgent()

    def test_parse_single_result(self):
        """Test parsing a single valid search result"""
        results = [{
            "title": "Python Developer - TechCorp",
            "url": "https://techcorp.com/jobs/123",
            "description": "We are looking for a Python developer in Tel Aviv with 3+ years experience"
        }]

        jobs = self.agent._parse_search_results(results, "Python Developer")

        assert len(jobs) == 1
        assert jobs[0].title == "Python Developer - TechCorp"
        assert jobs[0].company == "TechCorp"
        assert jobs[0].location == "Tel Aviv"
        assert jobs[0].url == "https://techcorp.com/jobs/123"
        assert jobs[0].source == "brave_search"
        assert "Python developer" in jobs[0].description

    def test_parse_multiple_results(self):
        """Test parsing multiple search results"""
        results = [
            {
                "title": "Backend Developer at Google",
                "url": "https://careers.google.com/jobs/1",
                "description": "Remote backend developer position"
            },
            {
                "title": "Frontend Engineer - Facebook",
                "url": "https://careers.facebook.com/jobs/2",
                "description": "Join our team in Jerusalem"
            }
        ]

        jobs = self.agent._parse_search_results(results, "Developer")

        assert len(jobs) == 2
        assert jobs[0].company == "Google"
        assert jobs[0].location == "Remote"
        assert jobs[1].company == "Facebook"
        assert jobs[1].location == "Jerusalem"

    def test_parse_result_with_missing_fields(self):
        """Test parsing result with missing optional fields"""
        results = [{
            "title": "Developer Position",
            "url": "https://example.com/job",
            # description missing
        }]

        jobs = self.agent._parse_search_results(results, "Developer")

        assert len(jobs) == 1
        assert jobs[0].title == "Developer Position"
        assert jobs[0].description == ""
        assert jobs[0].location == "Location not specified"

    def test_parse_empty_results(self):
        """Test parsing empty results list"""
        results = []
        jobs = self.agent._parse_search_results(results, "Developer")
        assert len(jobs) == 0

    def test_parse_result_with_invalid_data(self):
        """Test parsing handles invalid data gracefully"""
        results = [
            {"title": "Valid Job", "url": "https://example.com", "description": "Good job"},
            {"invalid": "data"},  # This should be skipped
            {"title": "Another Valid Job", "url": "https://example2.com", "description": "Great job"}
        ]

        jobs = self.agent._parse_search_results(results, "Developer")

        # Should skip the invalid entry
        assert len(jobs) == 2
        assert jobs[0].title == "Valid Job"
        assert jobs[1].title == "Another Valid Job"


class TestSearchJobsAPI:
    """Test the main search_jobs async method with API mocking"""

    @pytest.fixture
    def mock_response(self):
        """Create a mock response from Brave API"""
        return {
            "web": {
                "results": [
                    {
                        "title": "Python Developer - TechCorp",
                        "url": "https://techcorp.com/jobs/123",
                        "description": "Looking for Python developer in Tel Aviv"
                    },
                    {
                        "title": "Senior Python Engineer at StartupXYZ",
                        "url": "https://startupxyz.com/careers",
                        "description": "Remote Python position with great benefits"
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_success(self, mock_get, mock_response):
        """Test successful job search"""
        # Setup mock
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Python Developer", "Tel Aviv", 10)

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        assert call_args[0][0] == "https://api.search.brave.com/res/v1/web/search"
        assert call_args[1]['params']['q'].startswith("Python Developer")
        assert call_args[1]['params']['count'] == 10
        assert call_args[1]['headers']['X-Subscription-Token'] == "test_key"

        # Verify results
        assert len(jobs) == 2
        assert jobs[0].title == "Python Developer - TechCorp"
        assert jobs[1].company == "StartupXYZ"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_api_error(self, mock_get):
        """Test handling of API error response"""
        mock_get.return_value.status_code = 403
        mock_get.return_value.text = "Forbidden: Invalid API key"

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Developer", num_results=5)

        assert jobs == []

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_timeout(self, mock_get):
        """Test handling of request timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Developer")

        assert jobs == []

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_network_error(self, mock_get):
        """Test handling of network error"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Developer")

        assert jobs == []

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_max_results_limit(self, mock_get, mock_response):
        """Test that max results is capped at 20 (API limit)"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        await agent.search_jobs("Developer", num_results=50)

        # Check that count param was capped at 20
        call_args = mock_get.call_args
        assert call_args[1]['params']['count'] == 20

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_with_location_filter(self, mock_get, mock_response):
        """Test search with location parameter"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        await agent.search_jobs("Python Developer", location="Tel Aviv")

        # Verify location is included in query
        call_args = mock_get.call_args
        query = call_args[1]['params']['q']
        assert '"Tel Aviv"' in query

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_empty_results(self, mock_get):
        """Test handling of empty results from API"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"web": {"results": []}}

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("NonexistentJob123")

        assert jobs == []

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_jobs_malformed_response(self, mock_get):
        """Test handling of malformed API response"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"unexpected": "structure"}

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Developer")

        # Should handle gracefully and return empty list
        assert jobs == []


class TestSearchJobsForNews:
    """Test news search capabilities (using same search_jobs method)"""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_tech_news(self, mock_get):
        """Test searching for tech news articles"""
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "AI Breakthrough in 2024 - TechCrunch",
                        "url": "https://techcrunch.com/2024/ai-breakthrough",
                        "description": "Major advancement in artificial intelligence technology announced in Tel Aviv"
                    },
                    {
                        "title": "Startup Raises $100M - Globes",
                        "url": "https://globes.co.il/startup-funding",
                        "description": "Israeli startup secures funding for AI development in Jerusalem"
                    }
                ]
            }
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()

        # Use the search for tech news
        query = "AI technology Israel news"
        jobs = await agent.search_jobs(query, num_results=5)

        # Verify we got results
        assert len(jobs) == 2
        assert "AI" in jobs[0].title or "AI" in jobs[0].description

        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "AI technology Israel news" in call_args[1]['params']['q']

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_company_news(self, mock_get):
        """Test searching for company-specific news"""
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "Google Opens New Office - Calcalist",
                        "url": "https://calcalist.co.il/google-office",
                        "description": "Google announces new Tel Aviv office expansion with 500 new jobs"
                    }
                ]
            }
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        results = await agent.search_jobs("Google Israel news", num_results=5)

        assert len(results) == 1
        assert "Google" in results[0].title
        assert "Tel Aviv" in results[0].description

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_search_freshness_parameter(self, mock_get):
        """Test that freshness parameter is set correctly for recent news"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"web": {"results": []}}

        agent = BraveSearchAgent()
        await agent.search_jobs("tech news", num_results=10)

        # Verify freshness parameter is set to past month
        call_args = mock_get.call_args
        assert call_args[1]['params']['freshness'] == 'pm'


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios"""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_full_job_search_workflow(self, mock_get):
        """Test complete job search workflow"""
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "Senior Python Developer - Microsoft Israel",
                        "url": "https://careers.microsoft.com/il/jobs/123",
                        "description": "Join our Tel Aviv team. Remote work available. 5+ years experience required."
                    },
                    {
                        "title": "Python Engineer at Wix.com",
                        "url": "https://www.wix.com/jobs/positions/python-engineer",
                        "description": "Great position in Herzliya. Work on cutting-edge technology."
                    }
                ]
            }
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs(
            job_title="Python Developer",
            location="Israel",
            num_results=10
        )

        # Verify results are properly structured
        assert len(jobs) == 2

        # First job
        assert jobs[0].title == "Senior Python Developer - Microsoft Israel"
        assert jobs[0].company == "Microsoft Israel"
        assert jobs[0].location in ["Tel Aviv", "Remote"]  # Could match either
        assert jobs[0].source == "brave_search"
        assert jobs[0].url.startswith("https://")

        # Second job
        assert jobs[1].company == "Wix.com"
        assert jobs[1].location == "Herzliya"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"BRAVE_SEARCH_API_KEY": "test_key"})
    @patch('agents.brave_search.requests.get')
    async def test_resilience_to_partial_failures(self, mock_get):
        """Test that agent handles partial data gracefully"""
        mock_response = {
            "web": {
                "results": [
                    {
                        "title": "Good Job 1",
                        "url": "https://example1.com",
                        "description": "Valid job in Tel Aviv"
                    },
                    {
                        # Malformed - missing url
                        "title": "Bad Job",
                        "description": "Invalid"
                    },
                    {
                        "title": "Good Job 2",
                        "url": "https://example2.com",
                        "description": "Another valid job"
                    }
                ]
            }
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        agent = BraveSearchAgent()
        jobs = await agent.search_jobs("Developer")

        # Should successfully parse valid jobs despite one malformed entry
        assert len(jobs) >= 2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])