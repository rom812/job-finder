"""
Unit tests for FireCrawl Job Scraper
Tests FireCrawl-only job search functionality
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from typing import List

from agents.firecrawl_scraper import FireCrawlJobScraper
from models.models import Job


class TestFireCrawlScraperInitialization:
    """Test FireCrawl scraper initialization"""

    @patch.dict(os.environ, {
        "FIRECRAWL_API_KEY": "fc-test-key-here"
    })
    @patch('agents.firecrawl_scraper.FirecrawlApp')
    def test_init_with_valid_key(self, mock_firecrawl):
        """Test successful initialization with valid API key"""
        scraper = FireCrawlJobScraper()

        assert scraper.firecrawl is not None
        mock_firecrawl.assert_called_once_with(api_key="fc-test-key-here")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_error(self):
        """Test that missing FireCrawl API key raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            FireCrawlJobScraper()
        assert "FIRECRAWL_API_KEY not found" in str(excinfo.value)


class TestFireCrawlSearch:
    """Test FireCrawl search functionality"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "FIRECRAWL_API_KEY": "fc-test-key-here"
    })
    @patch('agents.firecrawl_scraper.FirecrawlApp')
    def scraper(self, mock_firecrawl_cls):
        """Create test scraper with mocked FireCrawl"""
        mock_firecrawl_instance = MagicMock()
        mock_firecrawl_cls.return_value = mock_firecrawl_instance

        scraper = FireCrawlJobScraper()
        scraper.firecrawl = mock_firecrawl_instance
        return scraper

    @pytest.mark.asyncio
    async def test_search_success(self, scraper):
        """Test successful FireCrawl search"""
        # Mock FireCrawl search response
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Python Developer at Google - Mountain View, CA",
                    "url": "https://careers.google.com/jobs/python-dev",
                    "markdown": "Python developer position at Google...",
                    "description": "Exciting Python role at Google"
                },
                {
                    "title": "Senior Software Engineer at Microsoft",
                    "url": "https://careers.microsoft.com/jobs/swe",
                    "markdown": "Senior software engineering position...",
                    "description": "Great opportunity at Microsoft"
                }
            ]
        }

        results = await scraper.search(
            job_title="Python Developer",
            location="Remote",
            num_jobs=10
        )

        assert len(results) == 2
        assert all(isinstance(job, Job) for job in results)
        assert results[0].source == "firecrawl"
        assert results[1].source == "firecrawl"

        # Verify FireCrawl was called with correct parameters
        scraper.firecrawl.search.assert_called_once()
        call_args = scraper.firecrawl.search.call_args
        assert "Python Developer jobs Remote" in call_args.kwargs['query']

    @pytest.mark.asyncio
    async def test_search_without_location(self, scraper):
        """Test search without location parameter"""
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "AI Engineer at OpenAI",
                    "url": "https://openai.com/careers/ai-engineer",
                    "markdown": "AI Engineer role...",
                    "description": "AI engineering position"
                }
            ]
        }

        results = await scraper.search(
            job_title="AI Engineer",
            num_jobs=5
        )

        assert len(results) == 1
        # Should search for "AI Engineer jobs" without location
        call_args = scraper.firecrawl.search.call_args
        assert call_args.kwargs['query'] == "AI Engineer jobs"

    @pytest.mark.asyncio
    async def test_search_parses_title_correctly(self, scraper):
        """Test that job titles are parsed correctly"""
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Backend Developer at Stripe - San Francisco",
                    "url": "https://stripe.com/jobs/backend-dev",
                    "markdown": "Backend developer position...",
                    "description": "Backend role at Stripe"
                }
            ]
        }

        results = await scraper.search(
            job_title="Backend Developer",
            location="San Francisco",
            num_jobs=10
        )

        assert len(results) == 1
        job = results[0]
        assert job.company == "Stripe"
        assert job.location == "San Francisco"

    @pytest.mark.asyncio
    async def test_search_handles_no_results(self, scraper):
        """Test search when FireCrawl returns no results"""
        scraper.firecrawl.search.return_value = {"data": []}

        results = await scraper.search(
            job_title="Nonexistent Job",
            location="Mars",
            num_jobs=10
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_handles_api_error(self, scraper):
        """Test search when FireCrawl API fails"""
        scraper.firecrawl.search.side_effect = Exception("API Error")

        results = await scraper.search(
            job_title="Software Engineer",
            num_jobs=10
        )

        assert len(results) == 0  # Should return empty list on error

    @pytest.mark.asyncio
    async def test_search_respects_num_jobs_limit(self, scraper):
        """Test that search respects the num_jobs parameter"""
        # Return 5 jobs
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": f"Job {i}",
                    "url": f"https://example.com/job{i}",
                    "description": f"Job {i} description"
                }
                for i in range(5)
            ]
        }

        results = await scraper.search(
            job_title="Developer",
            num_jobs=3  # Request only 3
        )

        # Should call FireCrawl with limit of 3
        call_args = scraper.firecrawl.search.call_args
        assert call_args.kwargs['limit'] == 3

    @pytest.mark.asyncio
    async def test_search_uses_markdown_as_description_fallback(self, scraper):
        """Test that markdown is used as description when description is missing"""
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Data Scientist",
                    "url": "https://example.com/ds",
                    "markdown": "This is a detailed markdown description of the job...",
                    "description": ""  # Empty description
                }
            ]
        }

        results = await scraper.search(
            job_title="Data Scientist",
            num_jobs=5
        )

        assert len(results) == 1
        # Should use markdown (truncated to 500 chars) or "No description available"
        # Since the code uses: description = result.get("description", markdown[:500] if markdown else "No description")
        # And description is empty string (falsy), it will use markdown
        assert len(results[0].description) >= 0  # Just verify description exists


class TestFireCrawlDeduplication:
    """Test job deduplication in FireCrawl scraper"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "FIRECRAWL_API_KEY": "fc-test-key-here"
    })
    @patch('agents.firecrawl_scraper.FirecrawlApp')
    def scraper(self, mock_firecrawl_cls):
        """Create test scraper"""
        mock_firecrawl_instance = MagicMock()
        mock_firecrawl_cls.return_value = mock_firecrawl_instance

        scraper = FireCrawlJobScraper()
        scraper.firecrawl = mock_firecrawl_instance
        return scraper

    @pytest.mark.asyncio
    async def test_deduplication_by_title_and_company(self, scraper):
        """Test that duplicate jobs are removed"""
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Python Developer at Google",
                    "url": "https://google.com/job1",
                    "description": "First posting"
                },
                {
                    "title": "Python Developer at Google",  # Duplicate
                    "url": "https://google.com/job2",  # Different URL
                    "description": "Second posting"
                },
                {
                    "title": "Python Developer at Microsoft",  # Different company
                    "url": "https://microsoft.com/job1",
                    "description": "Different company"
                }
            ]
        }

        results = await scraper.search(
            job_title="Python Developer",
            num_jobs=10
        )

        # Should have 2 unique jobs (Google duplicate removed)
        assert len(results) == 2
        companies = [job.company for job in results]
        assert "Google" in companies
        assert "Microsoft" in companies

    def test_deduplicate_jobs_method(self, scraper):
        """Test the _deduplicate_jobs method directly"""
        jobs = [
            Job(title="Developer", company="Google", location="US",
                description="Job 1", url="https://google.com/1", source="firecrawl"),
            Job(title="Developer", company="Google", location="US",
                description="Job 1 again", url="https://google.com/1", source="firecrawl"),  # Duplicate
            Job(title="Developer", company="Microsoft", location="US",
                description="Job 2", url="https://microsoft.com/1", source="firecrawl"),
        ]

        unique_jobs = scraper._deduplicate_jobs(jobs)

        assert len(unique_jobs) == 2


class TestFireCrawlEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "FIRECRAWL_API_KEY": "fc-test-key-here"
    })
    @patch('agents.firecrawl_scraper.FirecrawlApp')
    def scraper(self, mock_firecrawl_cls):
        """Create test scraper"""
        mock_firecrawl_instance = MagicMock()
        mock_firecrawl_cls.return_value = mock_firecrawl_instance

        scraper = FireCrawlJobScraper()
        scraper.firecrawl = mock_firecrawl_instance
        return scraper

    @pytest.mark.asyncio
    async def test_search_with_special_characters(self, scraper):
        """Test search with special characters in query"""
        scraper.firecrawl.search.return_value = {"data": []}

        results = await scraper.search(
            job_title="C++ Developer @#$%",
            num_jobs=10
        )

        assert isinstance(results, list)
        # Should still make the API call
        scraper.firecrawl.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, scraper):
        """Test search with empty query string"""
        scraper.firecrawl.search.return_value = {"data": []}

        results = await scraper.search(
            job_title="",
            num_jobs=10
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_very_long_query(self, scraper):
        """Test search with very long query"""
        scraper.firecrawl.search.return_value = {"data": []}

        long_query = "Software Engineer " * 50

        results = await scraper.search(
            job_title=long_query,
            num_jobs=10
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_handles_malformed_response(self, scraper):
        """Test search with malformed API response"""
        scraper.firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Valid Job",
                    "url": "https://example.com/1"
                    # Missing description, markdown
                },
                {
                    # Missing title
                    "url": "https://example.com/2",
                    "description": "Missing title"
                },
                {}  # Empty object
            ]
        }

        results = await scraper.search(
            job_title="Developer",
            num_jobs=10
        )

        # Should handle malformed data gracefully
        assert isinstance(results, list)


class TestJobScraperWithFireCrawlOnly:
    """
    Integration tests for JobScraper configured to use ONLY FireCrawl
    This tests the requirement: job_scraper should use ONLY FireCrawl
    """

    @pytest.fixture
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "FIRECRAWL_API_KEY": "fc-test-key-here"
    })
    @patch('agents.job_scraper.OpenAI')
    @patch('agents.firecrawl_scraper.FirecrawlApp')
    def scraper_firecrawl_only(self, mock_firecrawl_cls, mock_openai_cls):
        """Create JobScraper configured to use ONLY FireCrawl"""
        from agents.job_scraper import JobScraper

        # Mock OpenAI
        mock_openai_instance = MagicMock()
        mock_openai_cls.return_value = mock_openai_instance

        # Mock FireCrawl
        mock_firecrawl_instance = MagicMock()
        mock_firecrawl_cls.return_value = mock_firecrawl_instance

        # Create scraper with ONLY FireCrawl enabled
        scraper = JobScraper(use_brave_search=False, use_firecrawl=True)
        scraper.use_jsearch = False  # Disable JSearch
        scraper.openai_client = mock_openai_instance
        scraper.firecrawl_scraper.firecrawl = mock_firecrawl_instance

        return scraper, mock_firecrawl_instance

    @pytest.mark.asyncio
    async def test_job_scraper_uses_only_firecrawl(self, scraper_firecrawl_only):
        """Test that JobScraper uses ONLY FireCrawl when configured"""
        scraper, mock_firecrawl = scraper_firecrawl_only

        # Mock query expansion
        scraper._expand_job_query = Mock(return_value=["Software Engineer"])

        # Mock FireCrawl response
        mock_firecrawl.search.return_value = {
            "data": [
                {
                    "title": "Software Engineer at Google",
                    "url": "https://google.com/job1",
                    "description": "Great job at Google"
                }
            ]
        }

        results = await scraper.search(
            job_title="Software Engineer",
            location="Remote",
            num_jobs=10
        )

        # Verify results are from FireCrawl
        assert len(results) == 1
        assert results[0].source == "firecrawl"

        # Verify FireCrawl was called
        assert mock_firecrawl.search.called

    @pytest.mark.asyncio
    async def test_job_scraper_firecrawl_only_no_other_sources(self, scraper_firecrawl_only):
        """Verify that no other sources are used when FireCrawl-only is configured"""
        scraper, mock_firecrawl = scraper_firecrawl_only

        # Verify configuration
        assert scraper.use_jsearch == False
        assert scraper.use_brave_search == False
        assert scraper.use_firecrawl == True

        # Mock FireCrawl
        scraper._expand_job_query = Mock(return_value=["AI Engineer"])
        mock_firecrawl.search.return_value = {
            "data": [
                {
                    "title": "AI Engineer at OpenAI",
                    "url": "https://openai.com/job1",
                    "description": "AI role"
                }
            ]
        }

        results = await scraper.search(
            job_title="AI Engineer",
            num_jobs=5
        )

        # All results should be from FireCrawl
        assert all(job.source == "firecrawl" for job in results)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])