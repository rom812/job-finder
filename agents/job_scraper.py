"""
Agent 2: Job Scraper
Searches for jobs using JSearch API (RapidAPI)
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

from models.models import Job

# Load environment variables
load_dotenv()


class JobScraper:
    """
    Agent 2: Job Scraper

    Searches for jobs from job boards using JSearch API.
    Requires JSEARCH_API_KEY in environment variables.
    """

    def __init__(self):
        """Initialize the Job Scraper"""
        self.api_key = os.getenv("JSEARCH_API_KEY")
        self.api_host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")

        # Validate API key is present
        if not self.api_key:
            raise ValueError(
                "JSEARCH_API_KEY not found in environment variables. "
                "Please add it to your .env file. "
                "Get your key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch"
            )

    def _get_mock_jobs(self, job_title: str, location: Optional[str] = None, num_jobs: int = 20) -> List[Job]:
        """
        Generate mock job data for testing

        This simulates what JSearch API would return.
        Will be replaced with real API calls later.

        Args:
            job_title: Job title to search for
            location: Optional location filter
            num_jobs: Number of jobs to return

        Returns:
            List of Job objects
        """
        # Mock data - realistic job postings
        mock_jobs_data = [
            {
                "title": "Senior Python Developer",
                "company": "TechCorp Israel",
                "location": "Tel Aviv, Israel",
                "description": """
                We're looking for a Senior Python Developer to join our backend team.

                Requirements:
                - 5+ years of Python experience
                - Strong knowledge of Django/FastAPI
                - Experience with PostgreSQL, Redis
                - Docker, Kubernetes experience
                - AWS/GCP knowledge

                Nice to have:
                - Microservices architecture
                - Event-driven systems
                - LLM integration experience
                """,
                "url": "https://example.com/jobs/senior-python-dev-1",
                "posted_date": "2025-10-18",
                "source": "linkedin"
            },
            {
                "title": "Python Backend Engineer",
                "company": "StartupXYZ",
                "location": "Remote (Israel)",
                "description": """
                Join our fast-growing startup as a Backend Engineer!

                Requirements:
                - 3+ years Python experience
                - REST API design
                - SQL databases
                - Git, CI/CD

                We offer:
                - Remote work
                - Equity
                - Learning budget
                """,
                "url": "https://example.com/jobs/python-backend-2",
                "posted_date": "2025-10-19",
                "source": "indeed"
            },
            {
                "title": "Full Stack Developer (Python + Vue.js)",
                "company": "DataScience Ltd",
                "location": "Herzliya, Israel",
                "description": """
                Looking for a Full Stack Developer with Python and Vue.js experience.

                Requirements:
                - Python (Flask/FastAPI)
                - Vue.js 3
                - PostgreSQL
                - Docker

                Bonus:
                - Data visualization
                - ML/AI experience
                """,
                "url": "https://example.com/jobs/fullstack-vue-3",
                "posted_date": "2025-10-17",
                "source": "direct"
            },
            {
                "title": "Junior Python Developer",
                "company": "FinTech Solutions",
                "location": "Tel Aviv, Israel",
                "description": """
                Great opportunity for junior developers!

                Requirements:
                - 1-2 years Python experience
                - Understanding of OOP
                - Basic SQL knowledge
                - Willingness to learn

                We'll teach you:
                - Modern Python frameworks
                - Cloud technologies
                - DevOps practices
                """,
                "url": "https://example.com/jobs/junior-python-4",
                "posted_date": "2025-10-20",
                "source": "linkedin"
            },
            {
                "title": "Python AI/ML Engineer",
                "company": "AI Innovations",
                "location": "Remote",
                "description": """
                Build the future of AI with us!

                Requirements:
                - Strong Python skills
                - LangChain, OpenAI API experience
                - Vector databases (Pinecone, Weaviate)
                - REST APIs

                Exciting work:
                - LLM applications
                - Multi-agent systems
                - RAG implementations
                """,
                "url": "https://example.com/jobs/ai-ml-engineer-5",
                "posted_date": "2025-10-21",
                "source": "direct"
            },
            {
                "title": "DevOps Engineer (Python)",
                "company": "CloudTech",
                "location": "Raanana, Israel",
                "description": """
                DevOps role with strong Python automation focus.

                Requirements:
                - Python scripting
                - Docker, Kubernetes
                - AWS/Azure/GCP
                - CI/CD (Jenkins, GitLab)
                - Terraform, Ansible

                You'll work on:
                - Infrastructure automation
                - Monitoring systems
                - Deployment pipelines
                """,
                "url": "https://example.com/jobs/devops-python-6",
                "posted_date": "2025-10-16",
                "source": "indeed"
            }
        ]

        # Create Job objects from mock data
        jobs = []
        for job_data in mock_jobs_data[:num_jobs]:
            # Filter by location if specified
            if location and location.lower() not in job_data["location"].lower():
                continue

            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"].strip(),
                url=job_data["url"],
                posted_date=job_data.get("posted_date"),
                source=job_data.get("source", "direct")
            )
            jobs.append(job)

        return jobs

    async def _search_jsearch_api(self, job_title: str, location: Optional[str] = None, num_jobs: int = 20) -> List[Job]:
        """
        Search jobs using JSearch API (RapidAPI) with smart fallback strategy

        Args:
            job_title: Job title to search for
            location: Optional location filter
            num_jobs: Number of jobs to return

        Returns:
            List of Job objects
        """
        import requests

        url = "https://jsearch.p.rapidapi.com/search"

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }

        # Strategy 1: Try with location in query
        if location:
            query = f"{job_title} in {location}"
            print(f"🔍 Search Strategy 1: '{query}'")

            params = {
                "query": query,
                "page": "1",
                "num_pages": "1",
                "date_posted": "all"
            }

            response = requests.get(url, headers=headers, params=params)
            print(f"   📊 API Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                jobs_data = data.get("data", [])
                print(f"   ✅ Strategy 1 returned {len(jobs_data)} jobs")

                if len(jobs_data) > 0:
                    return self._convert_to_jobs(jobs_data, num_jobs)

            # Strategy 2: Try with Remote if original location failed
            if location.lower() not in ["remote", "worldwide"]:
                print(f"   💡 No results with location. Trying Strategy 2: '{job_title}' (Remote)")

                params = {
                    "query": f"{job_title} remote",
                    "page": "1",
                    "num_pages": "1",
                    "date_posted": "all",
                    "remote_jobs_only": "true"
                }

                response = requests.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    jobs_data = data.get("data", [])
                    print(f"   ✅ Strategy 2 returned {len(jobs_data)} jobs")

                    if len(jobs_data) > 0:
                        return self._convert_to_jobs(jobs_data, num_jobs)

        # Strategy 3: Try just the job title (global search)
        print(f"   💡 Trying Strategy 3: '{job_title}' (Global)")

        params = {
            "query": job_title,
            "page": "1",
            "num_pages": "1",
            "date_posted": "all"
        }

        response = requests.get(url, headers=headers, params=params)
        print(f"   📊 API Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            raise Exception(f"JSearch API error: {response.status_code} - {response.text}")

        data = response.json()
        jobs_data = data.get("data", [])
        print(f"   ✅ Strategy 3 returned {len(jobs_data)} jobs")

        if len(jobs_data) == 0:
            print(f"   ⚠️  No jobs found for '{job_title}'. Suggestions:")
            print(f"      - Try broader terms (e.g., 'Software Engineer' instead of 'AI Engineer')")
            print(f"      - Try different locations (e.g., 'United States', 'Remote')")
            print(f"      - Try related roles (e.g., 'Machine Learning Engineer', 'Data Scientist')")

        return self._convert_to_jobs(jobs_data, num_jobs)

    def _convert_to_jobs(self, jobs_data: list, num_jobs: int) -> List[Job]:
        """
        Convert JSearch API response to Job objects

        Args:
            jobs_data: Raw job data from API
            num_jobs: Maximum number of jobs to return

        Returns:
            List of Job objects
        """
        jobs = []
        for job_data in jobs_data[:num_jobs]:
            # Build location string
            city = job_data.get('job_city', '')
            country = job_data.get('job_country', '')
            state = job_data.get('job_state', '')

            if city and country:
                location = f"{city}, {country}"
            elif city and state:
                location = f"{city}, {state}"
            elif country:
                location = country
            elif job_data.get('job_is_remote'):
                location = "Remote"
            else:
                location = "Not specified"

            job = Job(
                title=job_data.get("job_title", "Unknown"),
                company=job_data.get("employer_name", "Unknown"),
                location=location,
                description=job_data.get("job_description", "No description available"),
                url=job_data.get("job_apply_link", ""),
                posted_date=job_data.get("job_posted_at_datetime_utc"),
                source="jsearch"
            )
            jobs.append(job)

        return jobs

    async def search(self, job_title: str, location: Optional[str] = None, num_jobs: int = 20) -> List[Job]:
        """
        Main method: Search for jobs using JSearch API

        Args:
            job_title: Job title to search for (e.g., "Python Developer")
            location: Optional location filter (e.g., "Tel Aviv")
            num_jobs: Number of jobs to return (default: 20)

        Returns:
            List of Job objects

        Example:
            scraper = JobScraper()
            jobs = await scraper.search("Python Developer", location="Tel Aviv", num_jobs=10)
        """
        print(f"🔍 Searching for: {job_title}")
        if location:
            print(f"📍 Location: {location}")
        print(f"📊 Requested jobs: {num_jobs}\n")

        # Use JSearch API
        jobs = await self._search_jsearch_api(job_title, location, num_jobs)

        print(f"✅ Found {len(jobs)} jobs!\n")

        return jobs


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio

    async def test():
        scraper = JobScraper()

        # Search for Python jobs
        jobs = await scraper.search(
            job_title="Python Developer",
            location="Tel Aviv",
            num_jobs=5
        )

        # Print results
        print("🎯 Job Search Results:")
        print("=" * 80)

        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location}")
            print(f"   Source: {job.source}")
            print(f"   Posted: {job.posted_date}")
            print(f"   URL: {job.url}")
            print(f"   Description: {job.description[:100]}...")

        print("\n" + "=" * 80)
        print(f"✅ Total jobs found: {len(jobs)}")

    asyncio.run(test())
