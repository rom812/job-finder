"""
Agent 3: News & Forum Intelligence
Collects information about companies from Reddit and news sources
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

from models.models import CompanyInsights

# Load environment variables
load_dotenv()


class NewsAgent:
    """
    Agent 3: News & Forum Intelligence

    Gathers company information from:
    - Reddit discussions (employee reviews, culture insights)
    - News articles (funding, growth, management changes)

    Returns structured CompanyInsights with sentiment analysis.
    Requires Reddit API credentials in environment variables.
    """

    def __init__(self):
        """
        Initialize the News Agent

        Raises:
            ValueError: If Reddit credentials are not found in environment variables
        """
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT")

        # Validate Reddit credentials are present
        if not self.reddit_client_id or not self.reddit_client_secret:
            raise ValueError(
                "Reddit API credentials not found in environment variables. "
                "Please add REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT to your .env file. "
                "Create a Reddit app at: https://www.reddit.com/prefs/apps"
            )

    def _get_mock_insights(self, company_name: str) -> CompanyInsights:
        """
        Generate mock company insights for testing

        This simulates what Reddit API would return.
        Will be replaced with real API calls later.

        Args:
            company_name: Name of the company to research

        Returns:
            CompanyInsights object
        """
        # Mock data - realistic company insights
        mock_insights = {
            "TechCorp Israel": {
                "sentiment": "positive",
                "highlights": [
                    "Great work-life balance, flexible hours",
                    "Modern tech stack (Python, Docker, K8s)",
                    "Generous learning budget and conference tickets",
                    "Collaborative team culture",
                    "Good salary but could be better"
                ],
                "news": [
                    "TechCorp raises $50M Series B funding (Oct 2025)",
                    "Launched new AI-powered platform",
                    "Expanded Tel Aviv office, hiring 50+ engineers"
                ],
                "culture": [
                    "Remote-first company",
                    "Strong focus on personal growth",
                    "Regular team events and hackathons"
                ]
            },
            "StartupXYZ": {
                "sentiment": "positive",
                "highlights": [
                    "Fast-paced startup environment",
                    "Equity for all employees",
                    "Fully remote team",
                    "Small team, lots of responsibility",
                    "Some reports of long hours during crunch"
                ],
                "news": [
                    "Closed seed round of $5M (Sep 2025)",
                    "First product launch scheduled for Q1 2026"
                ],
                "culture": [
                    "Startup culture - move fast, break things",
                    "Direct communication, flat hierarchy"
                ]
            },
            "DataScience Ltd": {
                "sentiment": "neutral",
                "highlights": [
                    "Interesting data projects",
                    "Good mentorship for junior developers",
                    "Office in Herzliya with hybrid work",
                    "Some bureaucracy typical of mid-size company",
                    "Competitive salary for market"
                ],
                "news": [
                    "DataScience Ltd partners with major bank",
                    "Published research paper at NeurIPS 2025"
                ],
                "culture": [
                    "Academic research culture",
                    "Focus on publishing and conferences"
                ]
            },
            "FinTech Solutions": {
                "sentiment": "positive",
                "highlights": [
                    "Very stable company, good for juniors",
                    "Structured onboarding and training",
                    "Regulated industry, thorough processes",
                    "Less cutting-edge tech than startups",
                    "Great benefits package"
                ],
                "news": [
                    "FinTech Solutions achieves SOC 2 compliance",
                    "Expanding to European market"
                ],
                "culture": [
                    "Professional corporate environment",
                    "Strong emphasis on security and compliance"
                ]
            },
            "AI Innovations": {
                "sentiment": "positive",
                "highlights": [
                    "Cutting-edge AI/ML work",
                    "Work with latest LLM technologies",
                    "Fully remote, global team",
                    "Fast-growing company, lots of opportunities",
                    "Competitive compensation + equity"
                ],
                "news": [
                    "AI Innovations launches GPT-powered product",
                    "Featured in TechCrunch for innovative multi-agent system",
                    "Hiring spree - 30 engineers in 6 months"
                ],
                "culture": [
                    "Research-driven culture",
                    "Encourages experimentation and innovation",
                    "Regular AI/ML paper reading groups"
                ]
            },
            "CloudTech": {
                "sentiment": "neutral",
                "highlights": [
                    "Solid DevOps practices and infrastructure",
                    "Good learning environment for cloud technologies",
                    "On-call rotation can be demanding",
                    "Mature company with established processes",
                    "Decent compensation"
                ],
                "news": [
                    "CloudTech migrates to multi-cloud architecture",
                    "Achieved 99.99% uptime last quarter"
                ],
                "culture": [
                    "DevOps culture with strong automation focus",
                    "24/7 operations with rotating on-call"
                ]
            }
        }

        # Get insights for this company, or return default
        insights = mock_insights.get(company_name, {
            "sentiment": "neutral",
            "highlights": [
                f"Limited public information about {company_name}",
                "Company appears to be well-established",
                "No major red flags found"
            ],
            "news": [
                f"{company_name} is actively hiring"
            ],
            "culture": [
                "General software company culture"
            ]
        })

        return CompanyInsights(
            company_name=company_name,
            reddit_sentiment=insights["sentiment"],
            reddit_highlights=insights["highlights"],
            recent_news=insights["news"],
            culture_notes=insights.get("culture", []),
            data_source="mock_data"
        )

    async def _search_reddit_praw(self, company_name: str) -> CompanyInsights:
        """
        Search Reddit using PRAW (Python Reddit API Wrapper)

        Args:
            company_name: Company to search for

        Returns:
            CompanyInsights object with real Reddit data
        """
        import praw

        print(f"   🔍 Connecting to Reddit API...")

        # Initialize Reddit client
        try:
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )

            # Test connection
            reddit.user.me()
            print(f"   ✅ Connected to Reddit!")

        except Exception as e:
            print(f"   ❌ Reddit connection failed: {e}")
            raise Exception(f"Failed to connect to Reddit API: {e}")

        # Search relevant subreddits
        subreddits = ["cscareerquestions", "experienceddevs", "programming", "jobs"]

        highlights = []
        sentiment_scores = []
        culture_notes = []

        print(f"   🔎 Searching {len(subreddits)} subreddits...")

        try:
            for subreddit_name in subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)

                    # Search for posts mentioning the company
                    for submission in subreddit.search(company_name, limit=5, time_filter="year"):
                        title = submission.title
                        text = f"{title} - {submission.selftext[:100]}" if submission.selftext else title

                        # Skip if too short
                        if len(text) < 20:
                            continue

                        highlights.append(text[:200])  # Limit length

                        # Simple sentiment analysis based on keywords
                        text_lower = text.lower()
                        positive_words = ["great", "love", "amazing", "best", "excellent", "good", "happy", "enjoy"]
                        negative_words = ["bad", "terrible", "worst", "avoid", "horrible", "toxic", "hate", "quit"]

                        positive_count = sum(1 for word in positive_words if word in text_lower)
                        negative_count = sum(1 for word in negative_words if word in text_lower)

                        if positive_count > negative_count:
                            sentiment_scores.append(1)
                        elif negative_count > positive_count:
                            sentiment_scores.append(-1)
                        else:
                            sentiment_scores.append(0)

                        # Extract culture notes from certain keywords
                        if any(word in text_lower for word in ["culture", "work-life", "remote", "benefits"]):
                            culture_notes.append(text[:150])

                except Exception as e:
                    print(f"   ⚠️  Error searching r/{subreddit_name}: {e}")
                    continue

        except Exception as e:
            print(f"   ❌ Reddit search failed: {e}")
            # Return neutral insights if search fails
            return CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[f"No Reddit discussions found for {company_name}"],
                recent_news=[],
                culture_notes=[],
                data_source="reddit_praw"
            )

        # Determine overall sentiment
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            if avg_sentiment > 0.2:
                sentiment = "positive"
            elif avg_sentiment < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        else:
            sentiment = "neutral"

        # If no results found, return neutral insights
        if not highlights:
            print(f"   📝 No Reddit results found for {company_name}")
            return CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[f"No Reddit discussions found for {company_name}"],
                recent_news=[],
                culture_notes=[],
                data_source="reddit_praw"
            )

        print(f"   ✅ Found {len(highlights)} Reddit posts")

        return CompanyInsights(
            company_name=company_name,
            reddit_sentiment=sentiment,
            reddit_highlights=highlights[:5],  # Top 5 insights
            recent_news=[f"Active discussions about {company_name} on Reddit"],
            culture_notes=culture_notes[:3],  # Top 3 culture notes
            data_source="reddit_praw"
        )

    async def get_insights(self, company_name: str) -> CompanyInsights:
        """
        Main method: Get company insights from Reddit

        Args:
            company_name: Name of the company to research

        Returns:
            CompanyInsights object with all gathered information

        Example:
            agent = NewsAgent()
            insights = await agent.get_insights("TechCorp Israel")
        """
        print(f"🔍 Researching company: {company_name}")

        # Use Reddit API
        insights = await self._search_reddit_praw(company_name)

        print(f"✅ Found insights for {company_name}!")
        print(f"   Sentiment: {insights.reddit_sentiment}")
        print(f"   Highlights: {len(insights.reddit_highlights)} items")
        print(f"   News: {len(insights.recent_news)} items\n")

        return insights


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = NewsAgent()

        # Test with multiple companies
        companies = [
            "TechCorp Israel",
            "StartupXYZ",
            "AI Innovations",
            "Unknown Company"
        ]

        print("🗞️  News & Forum Intelligence Agent Test")
        print("=" * 80)

        for company in companies:
            insights = await agent.get_insights(company)

            print(f"\n📊 Company: {insights.company_name}")
            print(f"   Sentiment: {insights.reddit_sentiment}")
            print(f"\n   💬 Reddit Highlights:")
            for highlight in insights.reddit_highlights[:3]:  # Show top 3
                print(f"      • {highlight}")

            if insights.recent_news:
                print(f"\n   📰 Recent News:")
                for news in insights.recent_news[:3]:
                    print(f"      • {news}")

            if insights.culture_notes:
                print(f"\n   🏢 Culture Notes:")
                for note in insights.culture_notes:
                    print(f"      • {note}")

            print("\n" + "-" * 80)

        print("\n✅ Agent 3 Test Complete!")

    asyncio.run(test())



