"""
Brave Search Agent
Uses Brave Search API to find job listings across the web
"""

import os
import json
from typing import List, Optional
from dotenv import load_dotenv
import requests

from models.models import Job

# Load environment variables
load_dotenv()


class BraveSearchAgent:
    """
    Brave Search Agent for Job Discovery

    Uses Brave Search API to find jobs from across the web:
    - Job boards (LinkedIn, Indeed, Glassdoor)
    - Company career pages
    - Israeli job sites (Drushim, AllJobs)
    - Tech community sites
    """

    def __init__(self):
        """Initialize Brave Search API client"""
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")

        if not self.api_key:
            raise ValueError(
                "BRAVE_SEARCH_API_KEY not found in environment variables.\n"
                "Get your FREE API key at: https://brave.com/search/api/"
            )

        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        print("✅ Brave Search API initialized")

    def _build_job_query(self, job_title: str, location: Optional[str] = None) -> str:
        """
        Build optimized search query for job hunting

        Args:
            job_title: Job title to search for
            location: Optional location filter

        Returns:
            Optimized search query string
        """
        # Build query that finds job postings, not people profiles
        query_parts = [job_title]

        # Add location if specified
        if location:
            query_parts.append(location)

        # Add specific job posting keywords and exclude profiles
        query_parts.append('"job posting" OR "careers" OR "apply now"')
        query_parts.append('-"linkedin.com/in/" -"profile" -"resume"')

        return " ".join(query_parts)

    async def search_company_info(
        self,
        company_name: str,
        num_results: int = 5
    ) -> List[dict]:
        """
        Search for information about a company

        Args:
            company_name: Name of the company to research
            num_results: Number of results to return (max 10)

        Returns:
            List of search results with title, url, and description

        Example:
            agent = BraveSearchAgent()
            results = await agent.search_company_info("Nvidia", 5)
        """
        # Build query focusing on company information
        query = f'"{company_name}" (about OR products OR services OR "what does")'

        print(f"\n🔍 Brave Search: Researching '{company_name}'...")

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        params = {
            "q": query,
            "count": min(num_results, 10),
            "search_lang": "en",
            "text_decorations": False,
            "spellcheck": True
        }

        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                print(f"   ❌ Brave Search error: {response.status_code}")
                return []

            data = response.json()
            results = data.get("web", {}).get("results", [])

            print(f"   ✅ Found {len(results)} results about {company_name}")

            # Return simplified results
            company_info = []
            for result in results:
                company_info.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", "")
                })

            return company_info

        except requests.exceptions.Timeout:
            print("   ❌ Brave Search timeout")
            return []
        except Exception as e:
            print(f"   ❌ Brave Search error: {str(e)}")
            return []

    async def search_jobs(
        self,
        job_title: str,
        location: Optional[str] = None,
        num_results: int = 20
    ) -> List[Job]:
        """
        Search for jobs using Brave Search API

        Args:
            job_title: Job title to search for (e.g., "Python Developer")
            location: Optional location (e.g., "Tel Aviv", "Remote")
            num_results: Number of results to return (max 20 per API call)

        Returns:
            List of Job objects

        Example:
            agent = BraveSearchAgent()
            jobs = await agent.search_jobs("Python Developer", "Tel Aviv", 10)
        """
        query = self._build_job_query(job_title, location)

        print(f"\n🔍 Brave Search: '{query}'")

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        params = {
            "q": query,
            "count": min(num_results, 20),  # Brave API max is 20 per request
            "search_lang": "en",  # Can also be "he" for Hebrew
            "freshness": "pm",  # Past month - more relevant jobs
            "text_decorations": False,
            "spellcheck": True
        }

        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=30
            )

            print(f"   📊 API Status: {response.status_code}")

            if response.status_code != 200:
                print(f"   ❌ Brave Search error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []

            data = response.json()
            results = data.get("web", {}).get("results", [])

            print(f"   ✅ Found {len(results)} results")

            # Convert to Job objects
            jobs = self._parse_search_results(results, job_title)

            return jobs

        except requests.exceptions.Timeout:
            print("   ❌ Brave Search timeout")
            return []
        except Exception as e:
            print(f"   ❌ Brave Search error: {str(e)}")
            return []

    def _parse_search_results(self, results: list, job_title: str) -> List[Job]:
        """
        Parse Brave Search results into Job objects

        Args:
            results: Raw results from Brave Search API
            job_title: Original job title query

        Returns:
            List of Job objects
        """
        jobs = []

        # Filter keywords that indicate this is NOT an actual job posting
        skip_keywords = [
            "how to hire",
            "hire developers",
            "hire python",
            "salary",
            "best websites",
            "top sites",
            "top 12 sites",
            "freelance",
            "guide",
            "tips",
            "tutorial",
            "course",
            "job description",
            "template",
            "vetted engineers"
        ]

        # NEW: Skip titles that indicate generic job board search results
        # These are search result pages, not individual job postings
        skip_title_patterns = [
            " jobs in ",              # "793 AI Engineer jobs in Paris"
            " Jobs in ",              # "937 AI Jobs in France"
            " job openings",          # "100 job openings in..."
            " Job Openings",
            "search results",
            "Search Results",
            " positions in ",
            " Positions in "
        ]

        # Skip URLs that are profiles, not job postings
        skip_url_patterns = [
            "linkedin.com/in/",      # Personal LinkedIn profiles
            "/profile/",             # General profile pages
            "/resume/",              # Resume pages
            "/cv/",                  # CV pages
            "/jobs?",                # LinkedIn/Indeed job search pages
            "/jobs/search",          # Job search result pages
            "glassdoor.com/Job/",    # Glassdoor search pages
        ]

        for result in results:
            try:
                # Extract data from search result
                title = result.get("title", "Unknown Position")
                url = result.get("url", "")
                description = result.get("description", "")

                # Skip LinkedIn profiles and similar
                if any(pattern in url.lower() for pattern in skip_url_patterns):
                    print(f"   ⏭️  Skipping profile/search page: {title[:50]}...")
                    continue

                # NEW: Skip generic job board search result pages (not individual jobs)
                if any(pattern in title for pattern in skip_title_patterns):
                    print(f"   ⏭️  Skipping job board search page: {title[:60]}...")
                    continue

                # Skip if this looks like an article about hiring, not a job posting
                title_lower = title.lower()
                if any(keyword in title_lower for keyword in skip_keywords):
                    print(f"   ⏭️  Skipping non-job result: {title[:60]}...")
                    continue

                # Try to extract company from URL or description
                company = self._extract_company(result)

                # Try to extract location from description
                location = self._extract_location(description)

                # Create Job object
                job = Job(
                    title=title,
                    company=company,
                    location=location or "Location not specified",
                    description=description,
                    url=url,
                    posted_date=None,  # Brave Search doesn't provide dates
                    source="brave_search"
                )

                jobs.append(job)

            except Exception as e:
                print(f"   ⚠️  Failed to parse result: {e}")
                continue

        return jobs

    def _extract_company(self, result: dict) -> str:
        """
        Try to extract company name from search result

        Args:
            result: Search result from Brave API

        Returns:
            Company name or "Unknown Company"
        """
        # Try to get from meta description
        title = result.get("title", "")
        url = result.get("url", "")

        # Common patterns in job posting titles
        # "Software Engineer - CompanyName"
        # "CompanyName is hiring: Software Engineer"

        if " - " in title:
            parts = title.split(" - ")
            if len(parts) > 1:
                return parts[-1].strip()

        if " at " in title:
            parts = title.split(" at ")
            if len(parts) > 1:
                return parts[-1].strip()

        # Try to extract from URL (e.g., linkedin.com/company/xyz)
        if "linkedin.com/company/" in url:
            company_slug = url.split("linkedin.com/company/")[1].split("/")[0]
            return company_slug.replace("-", " ").title()

        # Try to extract domain name as fallback
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. and .com/.co.il etc
            company = domain.replace("www.", "").split(".")[0]
            return company.title()
        except:
            pass

        return "Unknown Company"

    def _extract_location(self, text: str) -> Optional[str]:
        """
        Try to extract location from job description

        Args:
            text: Job description or title

        Returns:
            Location string or None
        """
        # Common Israeli cities
        israeli_cities = [
            "Tel Aviv", "Jerusalem", "Haifa", "Beer Sheva", "Herzliya",
            "Raanana", "Petah Tikva", "Rishon LeZion", "Netanya",
            "תל אביב", "ירושלים", "חיפה", "באר שבע"
        ]

        text_lower = text.lower()

        # Check for remote
        if any(word in text_lower for word in ["remote", "work from home", "wfh", "עבודה מהבית"]):
            return "Remote"

        # Check for Israeli cities
        for city in israeli_cities:
            if city.lower() in text_lower:
                return city

        # Check for Israel
        if "israel" in text_lower or "ישראל" in text_lower:
            return "Israel"

        return None


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = BraveSearchAgent()

        # Test search
        jobs = await agent.search_jobs(
            job_title="Python Developer",
            location="Tel Aviv",
            num_results=5
        )

        print("\n" + "=" * 80)
        print("🎯 Brave Search Results:")
        print("=" * 80)

        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location}")
            print(f"   URL: {job.url}")
            print(f"   Description: {job.description[:150]}...")

        print("\n" + "=" * 80)
        print(f"✅ Total jobs found: {len(jobs)}")

    asyncio.run(test())
