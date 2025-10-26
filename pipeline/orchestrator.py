"""
Pipeline Orchestrator
Coordinates all 4 agents to find and match jobs to a CV
"""

import asyncio
from typing import List, Optional
from pathlib import Path

from agents.cv_analyzer import CVAnalyzer
from agents.job_scraper import JobScraper
from agents.news_agent import NewsAgent
from agents.matcher import SmartMatcher
from models.models import CVAnalysis, Job, CompanyInsights, JobMatch


class JobFinderPipeline:
    """
    Main pipeline orchestrator for the job-finder system

    Coordinates all 4 agents:
    1. CV Analyzer - Analyzes CV and extracts structured data
    2. Job Scraper - Searches for jobs
    3. News Agent - Gathers company insights
    4. Smart Matcher - Matches CV to jobs and ranks them

    Example:
        pipeline = JobFinderPipeline()
        results = await pipeline.run(
            cv_path="cvs/my_cv.pdf",
            job_title="Python Developer",
            num_jobs=10
        )
    """

    def __init__(self):
        """
        Initialize the pipeline with all agents

        All agents use real APIs (JSearch, Reddit, OpenAI).
        Ensure all API keys are configured in .env file.
        """
        print("🚀 Initializing Job Finder Pipeline...")

        # Initialize all agents
        self.cv_analyzer = CVAnalyzer()
        self.job_scraper = JobScraper()
        self.news_agent = NewsAgent()
        self.matcher = SmartMatcher()

        print("✅ Pipeline initialized with 4 agents")

    async def run(
        self,
        cv_path: str,
        job_title: str,
        location: Optional[str] = None,
        num_jobs: int = 20
    ) -> List[JobMatch]:
        """
        Run the complete job-finding pipeline

        Args:
            cv_path: Path to CV PDF file
            job_title: Job title to search for (e.g., "Python Developer")
            location: Optional location filter (e.g., "Tel Aviv")
            num_jobs: Number of jobs to fetch (default: 20)

        Returns:
            List of JobMatch objects, sorted by score (highest first)

        Example:
            results = await pipeline.run(
                cv_path="cvs/my_cv.pdf",
                job_title="Python Developer",
                location="Tel Aviv",
                num_jobs=10
            )

            # Print top 5 matches
            for match in results[:5]:
                print(f"{match.job.title}: {match.match_score}/100")
        """
        print("\n" + "=" * 80)
        print("🎯 JOB FINDER PIPELINE - START")
        print("=" * 80)

        # Stage 1: Analyze CV and Search Jobs (in parallel!)
        print("\n📊 Stage 1: CV Analysis + Job Search (parallel)")
        print("-" * 80)

        cv_task = self._run_cv_analyzer(cv_path)
        jobs_task = self._run_job_scraper(job_title, location, num_jobs)

        # Run both in parallel using asyncio.gather
        cv_analysis, jobs = await asyncio.gather(cv_task, jobs_task)

        print(f"\n✅ Stage 1 Complete!")
        print(f"   CV Analysis: {len(cv_analysis.skills)} skills, {cv_analysis.experience_level} level")
        print(f"   Jobs Found: {len(jobs)} jobs")

        # Stage 2: Get Company Insights (parallel for all jobs)
        print("\n🗞️  Stage 2: Company Insights (parallel for all jobs)")
        print("-" * 80)

        company_insights = await self._run_news_agent(jobs)

        print(f"\n✅ Stage 2 Complete!")
        print(f"   Company Insights: {len(company_insights)} companies analyzed")

        # Stage 3: Match and Rank
        print("\n🎯 Stage 3: Smart Matching & Ranking")
        print("-" * 80)

        matches = await self._run_matcher(
            cv_analysis,
            jobs,
            company_insights,
            desired_role=job_title,
            desired_location=location or ""
        )

        print(f"\n✅ Stage 3 Complete!")
        print(f"   Matches Created: {len(matches)} jobs ranked")

        # Pipeline Complete!
        print("\n" + "=" * 80)
        print("🎉 PIPELINE COMPLETE!")
        print("=" * 80)

        return matches

    async def _run_cv_analyzer(self, cv_path: str) -> CVAnalysis:
        """
        Stage 1a: Analyze CV

        Args:
            cv_path: Path to CV PDF

        Returns:
            CVAnalysis object
        """
        print(f"\n📄 Agent 1: CV Analyzer")
        print(f"   CV Path: {cv_path}")

        cv_analysis = await self.cv_analyzer.analyze(cv_path)

        return cv_analysis

    async def _run_job_scraper(
        self,
        job_title: str,
        location: Optional[str],
        num_jobs: int
    ) -> List[Job]:
        """
        Stage 1b: Search for jobs

        Args:
            job_title: Job title to search
            location: Optional location
            num_jobs: Number of jobs

        Returns:
            List of Job objects
        """
        print(f"\n🔍 Agent 2: Job Scraper")
        print(f"   Searching: {job_title}")
        if location:
            print(f"   Location: {location}")
        print(f"   Number of jobs: {num_jobs}")

        jobs = await self.job_scraper.search(job_title, location, num_jobs)

        return jobs

    async def _run_news_agent(self, jobs: List[Job]) -> List[CompanyInsights]:
        """
        Stage 2: Get company insights for all jobs (in parallel)

        Args:
            jobs: List of Job objects

        Returns:
            List of CompanyInsights objects
        """
        print(f"\n🗞️  Agent 3: News Agent")
        print(f"   Analyzing {len(jobs)} companies...")

        # Create tasks for all companies (parallel!)
        tasks = [
            self.news_agent.get_insights(job.company)
            for job in jobs
        ]

        # Run all in parallel
        company_insights = await asyncio.gather(*tasks)

        return company_insights

    async def _run_matcher(
        self,
        cv_analysis: CVAnalysis,
        jobs: List[Job],
        company_insights: List[CompanyInsights],
        desired_role: str = "",
        desired_location: str = ""
    ) -> List[JobMatch]:
        """
        Stage 3: Match CV to jobs and rank

        Args:
            cv_analysis: Analyzed CV
            jobs: List of jobs
            company_insights: List of company insights
            desired_role: User's desired job role
            desired_location: User's preferred location

        Returns:
            List of JobMatch objects, sorted by score
        """
        print(f"\n🎯 Agent 4: Smart Matcher")
        print(f"   Matching {len(jobs)} jobs to CV...")

        matches = await self.matcher.match_and_rank(
            cv_analysis,
            jobs,
            company_insights,
            desired_role=desired_role,
            desired_location=desired_location
        )

        return matches

    def print_results(self, matches: List[JobMatch], top_n: int = 10):
        """
        Print formatted results with enhanced display

        Args:
            matches: List of JobMatch objects
            top_n: Number of top matches to display
        """
        print("\n" + "=" * 100)
        print(f"📊 TOP {min(top_n, len(matches))} JOB MATCHES")
        print("=" * 100)

        for i, match in enumerate(matches[:top_n], 1):
            # Header with job title and score
            print(f"\n{'━' * 100}")
            print(f"#{i} | {match.job.title}")
            print(f"{'━' * 100}")

            # Basic info
            print(f"🏢 Company:        {match.job.company}")
            print(f"📍 Location:       {match.job.location}")
            print(f"📅 Posted:         {match.job.posted_date or 'Recently'}")
            print(f"🎯 Match Score:    {match.match_score:.1f}/100 - {match.recommendation}")

            # Job description preview (first 400 chars)
            print(f"\n📋 Job Description:")
            desc_preview = match.job.description.strip()[:400]
            # Clean up the description formatting
            desc_lines = [line.strip() for line in desc_preview.split('\n') if line.strip()]
            print(f"   {' '.join(desc_lines[:3])}...")

            # Skills analysis
            print(f"\n🔧 Skills Analysis:")
            if match.skill_overlap:
                print(f"   ✅ You Have: {', '.join(match.skill_overlap[:8])}")
            else:
                print(f"   ✅ You Have: (analyzing...)")

            if match.skill_gaps:
                print(f"   📚 To Learn: {', '.join(match.skill_gaps[:5])}")
            else:
                print(f"   📚 To Learn: None identified")

            # Match reasoning
            print(f"\n💡 Why This Match:")
            for reason in match.reasoning[:4]:
                print(f"   • {reason}")

            # Reddit & company insights
            print(f"\n🗣️  Company Insights (Reddit):")
            print(f"   Overall Sentiment: {match.company_insights.reddit_sentiment.upper()}")

            if match.company_insights.reddit_highlights:
                print(f"   Recent Discussions:")
                for j, highlight in enumerate(match.company_insights.reddit_highlights[:2], 1):
                    clean_highlight = highlight.strip()[:180]
                    print(f"      {j}. {clean_highlight}...")

            if match.company_insights.culture_notes:
                print(f"   Culture Notes:")
                for note in match.company_insights.culture_notes[:2]:
                    clean_note = note.strip()[:150]
                    print(f"      • {clean_note}...")

            # Application link - HIGHLIGHTED
            print(f"\n{'─' * 100}")
            print(f"🚀 APPLY HERE: {match.job.url}")
            print(f"{'─' * 100}")

        print("\n" + "=" * 100)
        print("✅ End of results")
        print("=" * 100)


# Example usage
if __name__ == "__main__":
    async def main():
        # Interactive user input
        print("=" * 80)
        print("🎯 JOB FINDER - INTERACTIVE MODE")
        print("=" * 80)
        print()

        # Get user inputs
        cv_path = input("📄 CV Path [cvs/romCV.pdf]: ").strip() or "cvs/romCV.pdf"

        print("\n💡 Common roles: Software Engineer, Backend Developer, Data Scientist, DevOps Engineer, Full Stack Developer")
        job_role = input("💼 What role are you searching for? ").strip()

        print("\n💡 Best results: United States, Remote, Germany, Canada, United Kingdom")
        country = input("🌍 Which country/location? ").strip()

        num_jobs_input = input("\n📊 How many jobs to analyze? [20]: ").strip() or "20"

        # Validate num_jobs
        try:
            num_jobs = int(num_jobs_input)
            if num_jobs <= 0:
                print("⚠️  Invalid number, using default: 20")
                num_jobs = 20
        except ValueError:
            print("⚠️  Invalid number, using default: 20")
            num_jobs = 20

        # Confirm inputs
        print("\n" + "-" * 80)
        print("📋 Search Configuration:")
        print(f"   CV: {cv_path}")
        print(f"   Role: {job_role}")
        print(f"   Location: {country}")
        print(f"   Jobs to analyze: {num_jobs}")
        print("-" * 80)
        print()

        # Create pipeline (uses real APIs)
        pipeline = JobFinderPipeline()

        # Run pipeline
        results = await pipeline.run(
            cv_path=cv_path,
            job_title=job_role,
            location=country,
            num_jobs=num_jobs
        )

        # Print results
        pipeline.print_results(results, top_n=5)

        # Additional analysis
        print("\n📈 SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total jobs analyzed: {len(results)}")

        if results:
            print(f"Average match score: {sum(m.match_score for m in results) / len(results):.1f}/100")
            print(f"Strong matches (80+): {sum(1 for m in results if m.match_score >= 80)}")
            print(f"Good fits (65-79): {sum(1 for m in results if 65 <= m.match_score < 80)}")
            print(f"Worth considering (50-64): {sum(1 for m in results if 50 <= m.match_score < 65)}")
            print(f"Skip (<50): {sum(1 for m in results if m.match_score < 50)}")
        else:
            print("Average match score: N/A (no jobs found)")
            print("💡 Try a different search query or location!")

    asyncio.run(main())
