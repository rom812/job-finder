"""
FireCrawl Job Scraper Agent
Uses FireCrawl API with web search to find job listings
This replaces JSearch API with a more flexible web scraping approach
"""

import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

from models.models import Job

# Load environment variables
load_dotenv()


class FireCrawlJobScraper:
    """
    Job scraper using FireCrawl API with search functionality

    Uses FireCrawl's search feature to find jobs across the web,
    then scrapes and extracts structured data from job listings.

    Requires FIRECRAWL_API_KEY in environment variables.
    """

    def __init__(self):
        """
        Initialize the FireCrawl Job Scraper

        Requires:
            - FIRECRAWL_API_KEY in environment
        """
        # FireCrawl setup
        firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)
        print("✅ FireCrawl API initialized")

    async def search(
        self,
        job_title: str,
        location: Optional[str] = None,
        num_jobs: int = 20
    ) -> List[Job]:
        """
        Search for jobs using FireCrawl's Search API

        Uses FireCrawl to search the web for job listings and extract structured data.

        Args:
            job_title: Job title to search for (e.g., "Python Developer")
            location: Optional location filter (e.g., "Tel Aviv", "Remote")
            num_jobs: Total number of jobs to return (default: 20)

        Returns:
            List of Job objects

        Example:
            scraper = FireCrawlJobScraper()
            jobs = await scraper.search(
                job_title="Software Engineer",
                location="Remote",
                num_jobs=20
            )
        """
        print(f"\n🔥 FireCrawl Search Started")
        print(f"   Query: '{job_title}'")
        if location:
            print(f"   Location: {location}")
        print(f"   Requested: {num_jobs} jobs")

        try:
            # Build search query
            if location:
                search_query = f"{job_title} jobs {location}"
            else:
                search_query = f"{job_title} jobs"

            print(f"   Search Query: '{search_query}'")

            # Use FireCrawl search to find job listings
            search_results = self.firecrawl.search(
                query=search_query,
                limit=min(num_jobs, 10),  # FireCrawl limits per API call
            )

            # Extract web results from SearchData object
            web_results = search_results.web if hasattr(search_results, 'web') and search_results.web else []
            print(f"   ✅ FireCrawl returned {len(web_results)} results")

            # Extract job data from search results
            jobs = []
            for result in web_results:
                # Extract basic info from search result
                # result is a SearchResultWeb object with url, title, description attributes
                title = result.title if hasattr(result, 'title') else "Unknown Job"
                url = result.url if hasattr(result, 'url') else ""
                description = result.description if hasattr(result, 'description') else "No description"

                # Try to extract company and location from title or content
                # Typical format: "Job Title at Company - Location"
                company = "Unknown Company"
                job_location = location or "Not specified"

                # Simple parsing of title (can be enhanced with AI later)
                if " at " in title:
                    parts = title.split(" at ", 1)
                    job_title_part = parts[0].strip()
                    company_part = parts[1].strip()

                    if " - " in company_part:
                        company, job_location = company_part.split(" - ", 1)
                        company = company.strip()
                        job_location = job_location.strip()
                    else:
                        company = company_part

                job = Job(
                    title=title,
                    company=company,
                    location=job_location,
                    description=description,
                    url=url,
                    posted_date=None,  # Not available from search results
                    source="firecrawl"
                )
                jobs.append(job)

            # Deduplicate jobs
            unique_jobs = self._deduplicate_jobs(jobs)

            print(f"\n✅ FireCrawl Search Complete")
            print(f"   Total jobs found: {len(jobs)}")
            print(f"   Unique jobs: {len(unique_jobs)}")
            print(f"   Returning: {len(unique_jobs)} jobs\n")

            return unique_jobs

        except Exception as e:
            print(f"   ❌ FireCrawl search failed: {str(e)}")
            return []

    def _deduplicate_jobs(self, jobs: List[Job]) -> List[Job]:
        """
        Remove duplicate jobs based on title and company

        Args:
            jobs: List of Job objects

        Returns:
            Deduplicated list of Job objects
        """
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create a unique identifier
            job_id = (job.title.lower().strip(), job.company.lower().strip())

            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)

        return unique_jobs


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        scraper = FireCrawlJobScraper()

        # Search for remote Python jobs
        jobs = await scraper.search(
            job_title="Python Developer",
            location="Remote",
            num_jobs=10
        )

        # Print results
        print("\n" + "=" * 80)
        print("🎯 FireCrawl Job Search Results")
        print("=" * 80)

        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location}")
            print(f"   Source: {job.source}")
            print(f"   URL: {job.url}")
            print(f"   Description: {job.description[:150]}...")

        print("\n" + "=" * 80)
        print(f"✅ Total jobs found: {len(jobs)}")

    asyncio.run(test())