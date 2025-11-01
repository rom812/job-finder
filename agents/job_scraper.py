"""
Agent 2: Job Scraper
Searches for jobs using multiple sources:
- JSearch API (job boards)
- Brave Search (web-wide search)
With smart query expansion that expands informal queries to formal job titles
"""

import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

from models.models import Job
from agents.brave_search import BraveSearchAgent
from agents.firecrawl_scraper import FireCrawlJobScraper

# Load environment variables
load_dotenv()


class JobScraper:
    """
    Agent 2: Job Scraper

    Searches for jobs from multiple sources:
    - JSearch API (job boards)
    - Brave Search API (web-wide search)

    Requires API keys in environment variables.
    """

    def __init__(self, use_brave_search: bool = True, use_firecrawl: bool = True):
        """
        Initialize the Job Scraper with multiple search sources

        Args:
            use_brave_search: Whether to include Brave Search results (default: True)
            use_firecrawl: Whether to include FireCrawl results (default: True)
        """
        # OpenAI setup (for query expansion)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.openai_client = OpenAI(api_key=openai_api_key)
        print("✅ OpenAI initialized (for smart query expansion)")

        # JSearch setup
        self.jsearch_api_key = os.getenv("JSEARCH_API_KEY")
        self.jsearch_api_host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")

        if not self.jsearch_api_key:
            print("⚠️  JSEARCH_API_KEY not found - JSearch will be skipped")
            self.use_jsearch = False
        else:
            self.use_jsearch = True
            print("✅ JSearch API initialized")

        # Brave Search setup
        self.use_brave_search = use_brave_search
        if use_brave_search:
            try:
                self.brave_agent = BraveSearchAgent()
                print("✅ Brave Search initialized")
            except ValueError as e:
                print(f"⚠️  Brave Search not available: {e}")
                self.use_brave_search = False

        # FireCrawl setup
        self.use_firecrawl = use_firecrawl
        if use_firecrawl:
            try:
                self.firecrawl_scraper = FireCrawlJobScraper()
                print("✅ FireCrawl initialized")
            except ValueError as e:
                print(f"⚠️  FireCrawl not available: {e}")
                self.use_firecrawl = False

    def _expand_job_query(self, user_query: str, experience_level: str = "Mid") -> List[str]:
        """
        Expand informal user query to formal job titles using OpenAI

        Example:
            Input: "ai student"
            Output: ["AI Intern", "Junior AI Engineer", "AI Research Assistant", "Machine Learning Intern"]

        Args:
            user_query: Informal job search query from user
            experience_level: Experience level ("Junior", "Mid", "Senior", "Lead")

        Returns:
            List of formal job titles (3-5 variations)
        """
        print(f"🤖 Expanding query: '{user_query}' (Level: {experience_level})...")

        # Adjust prompt based on experience level
        level_guidance = {
            "Junior": "Focus on entry-level positions like: Junior, Associate, Entry Level, Graduate roles",
            "Mid": "Focus on mid-level positions like: Developer, Engineer, Specialist (no seniority prefix)",
            "Senior": "Focus on senior positions like: Senior, Lead, Principal, Staff Engineer",
            "Lead": "Focus on leadership positions like: Lead, Principal, Staff, Engineering Manager"
        }

        guidance = level_guidance.get(experience_level, level_guidance["Mid"])

        prompt = f"""
You are a job search expert. Convert this job search query into 3-5 formal, professional job titles appropriate for a {experience_level} level candidate.

User query: "{user_query}"
Experience Level: {experience_level}

{guidance}

Return ONLY a JSON array of formal job titles, nothing else.

Example for Junior level:
User query: "Backend Developer"
Output: ["Junior Backend Developer", "Backend Developer - Entry Level", "Associate Backend Engineer", "Backend Software Engineer - Junior"]

Example for Mid level:
User query: "Backend Developer"
Output: ["Backend Developer", "Backend Software Engineer", "Server-Side Developer", "Backend Engineer"]

Example for Senior level:
User query: "Backend Developer"
Output: ["Senior Backend Developer", "Senior Backend Engineer", "Lead Backend Developer", "Principal Backend Engineer"]

Now convert for {experience_level} level: "{user_query}"
Output:
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )

            result = response.choices[0].message.content.strip()

            # Remove markdown code block if present (```json ... ```)
            if result.startswith("```"):
                # Remove first line (```json or ```), last line (```), and parse middle
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1]).strip()

            # Parse JSON array
            job_titles = json.loads(result)

            print(f"   ✅ Expanded to {len(job_titles)} queries: {', '.join(job_titles)}")
            return job_titles

        except Exception as e:
            print(f"   ⚠️  Query expansion failed: {e}")
            print(f"   → Using original query: '{user_query}'")
            return [user_query]  # Fallback to original

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
            "X-RapidAPI-Key": self.jsearch_api_key,
            "X-RapidAPI-Host": self.jsearch_api_host
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

    async def _search_adzuna_api(self, job_title: str, location: Optional[str] = None, num_jobs: int = 20) -> List[Job]:
        """
        Search jobs using Adzuna API
        EXCELLENT for Israeli jobs! Supports country=il natively.

        Args:
            job_title: Job title to search for (e.g., "Python Developer")
            location: Optional location filter (e.g., "Tel Aviv", "Jerusalem")
            num_jobs: Number of jobs to return (default: 20)

        Returns:
            List of Job objects
        """
        if not self.adzuna_app_id or not self.adzuna_app_key:
            print("⚠️  Adzuna API not configured, skipping...")
            return []

        import requests

        print(f"🔍 Searching Adzuna for: {job_title}")
        if location:
            print(f"📍 Location: {location}")

        # Determine country code
        # If location contains Israel-related terms, use "il" (Israel)
        country = "il"  # Default to Israel
        if location:
            location_lower = location.lower()
            if any(term in location_lower for term in ["israel", "ישראל", "tel aviv", "jerusalem", "haifa"]):
                country = "il"

        # Build API URL
        # Format: https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
        page = 1
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

        # Build parameters
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "what": job_title,  # Job search keyword
            "results_per_page": min(num_jobs, 50),  # Max 50 per page
            "content-type": "application/json"
        }

        # Add location if specified
        if location:
            params["where"] = location

        try:
            print(f"🚀 Calling Adzuna API (country={country})")
            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                print(f"❌ Adzuna API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []

            data = response.json()
            results = data.get("results", [])

            print(f"✅ Adzuna returned {len(results)} jobs from Israel")

            # Convert to Job objects
            jobs = []
            for item in results[:num_jobs]:
                # Extract location
                location_display = item.get("location", {}).get("display_name", location or "Israel")

                # Extract description
                description = item.get("description", "No description available")

                # Build job object
                job = Job(
                    title=item.get("title", "Unknown"),
                    company=item.get("company", {}).get("display_name", "Unknown"),
                    location=location_display,
                    description=description,
                    url=item.get("redirect_url", ""),
                    posted_date=item.get("created"),
                    source="adzuna"
                )
                jobs.append(job)

            return jobs

        except requests.exceptions.Timeout:
            print("❌ Adzuna API timeout")
            return []
        except Exception as e:
            print(f"❌ Adzuna API error: {str(e)}")
            return []

    async def search(
        self,
        job_title: str,
        location: Optional[str] = None,
        num_jobs: int = 20,
        experience_level: str = "Mid"
    ) -> List[Job]:
        """
        Main method: Search for jobs with SMART QUERY EXPANSION + MULTI-SOURCE SEARCH

        Strategy:
        1. Expand user query to 3-5 formal job titles (e.g., "ai student" → ["AI Intern", "Junior AI Engineer", ...])
        2. Search each expanded query via:
           - JSearch API (job boards)
           - Brave Search (web-wide)
        3. Combine and deduplicate results

        Args:
            job_title: Job title to search for (informal OK! e.g., "ai student", "python dev")
            location: Optional location filter (e.g., "Israel", "Tel Aviv", "Remote")
            num_jobs: Number of jobs to return (default: 20)
            experience_level: Experience level to target ("Junior", "Mid", "Senior", "Lead")

        Returns:
            List of Job objects

        Example:
            scraper = JobScraper()
            jobs = await scraper.search("ai student", location="Remote", num_jobs=10, experience_level="Junior")
        """
        print(f"\n🔍 Smart Job Search Started")
        print(f"   User Query: '{job_title}'")
        if location:
            print(f"   Location: {location}")
        print(f"   Requested: {num_jobs} jobs")
        print(f"   Experience Level: {experience_level}")
        print(f"   Sources: ", end="")
        sources = []
        if self.use_jsearch:
            sources.append("JSearch")
        if self.use_brave_search:
            sources.append("Brave Search")
        print(", ".join(sources) + "\n")

        # Step 1: Expand query to multiple formal job titles with experience level targeting
        expanded_queries = self._expand_job_query(job_title, experience_level)

        # Step 2: Calculate how many jobs to get from each source
        active_sources = sum([self.use_jsearch, self.use_brave_search, self.use_firecrawl])

        if active_sources == 0:
            print("   ❌ No job search sources available!")
            return []

        # Split jobs evenly between sources
        jobs_per_source = num_jobs // active_sources if active_sources > 0 else num_jobs

        # Collect jobs from each source separately to ensure balanced results
        jsearch_all_jobs = []
        brave_all_jobs = []
        firecrawl_all_jobs = []

        # Step 2: Search each expanded query across multiple sources
        jobs_per_query = max(5, jobs_per_source // len(expanded_queries))  # Get at least 5 per query

        for i, query in enumerate(expanded_queries, 1):
            print(f"\n📋 Query {i}/{len(expanded_queries)}: '{query}'")

            # Search JSearch if available
            if self.use_jsearch:
                try:
                    jsearch_jobs = await self._search_jsearch_api(query, location, jobs_per_query)
                    jsearch_all_jobs.extend(jsearch_jobs)
                    print(f"   ✅ JSearch: {len(jsearch_jobs)} jobs")
                except Exception as e:
                    print(f"   ⚠️  JSearch failed: {e}")

            # Search Brave Search if available
            if self.use_brave_search:
                try:
                    brave_jobs = await self.brave_agent.search_jobs(query, location, jobs_per_query)
                    brave_all_jobs.extend(brave_jobs)
                    print(f"   ✅ Brave Search: {len(brave_jobs)} jobs")
                except Exception as e:
                    print(f"   ⚠️  Brave Search failed: {e}")

            # Search FireCrawl if available
            if self.use_firecrawl:
                try:
                    firecrawl_jobs = await self.firecrawl_scraper.search(query, location, jobs_per_query)
                    firecrawl_all_jobs.extend(firecrawl_jobs)
                    print(f"   ✅ FireCrawl: {len(firecrawl_jobs)} jobs")
                except Exception as e:
                    print(f"   ⚠️  FireCrawl failed: {e}")

        # Step 3: Deduplicate each source separately
        def deduplicate_jobs(jobs_list):
            seen_urls = set()
            seen_jobs = set()
            unique = []

            for job in jobs_list:
                job_id = (job.title.lower(), job.company.lower())

                if job.url and job.url in seen_urls:
                    continue
                if job_id in seen_jobs:
                    continue

                if job.url:
                    seen_urls.add(job.url)
                seen_jobs.add(job_id)
                unique.append(job)

            return unique

        # Deduplicate each source
        jsearch_unique = deduplicate_jobs(jsearch_all_jobs)
        brave_unique = deduplicate_jobs(brave_all_jobs)
        firecrawl_unique = deduplicate_jobs(firecrawl_all_jobs)

        # Step 4: Distribute jobs evenly from all active sources
        final_jobs = []

        # Add from each source proportionally
        if active_sources > 0:
            jsearch_limit = min(len(jsearch_unique), jobs_per_source) if self.use_jsearch else 0
            brave_limit = min(len(brave_unique), jobs_per_source) if self.use_brave_search else 0
            firecrawl_limit = min(len(firecrawl_unique), jobs_per_source) if self.use_firecrawl else 0

            # If one source has fewer jobs, redistribute to others
            total_available = jsearch_limit + brave_limit + firecrawl_limit
            if total_available < num_jobs:
                # Take all available
                final_jobs.extend(jsearch_unique[:jsearch_limit])
                final_jobs.extend(brave_unique[:brave_limit])
                final_jobs.extend(firecrawl_unique[:firecrawl_limit])
            else:
                # Distribute evenly
                final_jobs.extend(jsearch_unique[:jsearch_limit])
                final_jobs.extend(brave_unique[:brave_limit])
                final_jobs.extend(firecrawl_unique[:firecrawl_limit])

        print(f"\n✅ Total unique jobs found: {len(final_jobs)}")
        print(f"   Original query: '{job_title}'")
        print(f"   Expanded to: {len(expanded_queries)} searches")
        print(f"   Sources: {', '.join(sources)}")
        if self.use_jsearch:
            print(f"   JSearch: {len(jsearch_unique)} unique")
        if self.use_brave_search:
            print(f"   Brave Search: {len(brave_unique)} unique")
        if self.use_firecrawl:
            print(f"   FireCrawl: {len(firecrawl_unique)} unique")
        print(f"   Result: {len(final_jobs)} total jobs\n")

        return final_jobs[:num_jobs]


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
