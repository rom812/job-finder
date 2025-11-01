"""
Agent 3: News & Forum Intelligence
Collects information about companies using FireCrawl web search
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from firecrawl import FirecrawlApp

from models.models import CompanyInsights

# Load environment variables
load_dotenv()


class NewsAgent:
    """
    Agent 3: News & Forum Intelligence

    Gathers company information from:
    - FireCrawl web search (company reviews, news, culture insights)
    - News articles (funding, growth, management changes)

    Returns structured CompanyInsights with sentiment analysis.
    Requires FireCrawl API key in environment variables.
    """

    def __init__(self):
        """
        Initialize the News Agent

        Raises:
            ValueError: If FireCrawl API key is not found in environment variables
        """
        # Initialize FireCrawl for web research
        firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY not found in environment variables. "
                "Please add FIRECRAWL_API_KEY to your .env file. "
                "Get your API key at: https://www.firecrawl.dev/"
            )

        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)
        print("✅ FireCrawl initialized for company research")

        # Initialize OpenAI client for intelligent analysis
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
            print("✅ OpenAI initialized for AI analysis")
        else:
            print("⚠️  Warning: OPENAI_API_KEY not found - AI analysis will be disabled")
            self.openai_client = None

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

    async def _search_firecrawl(self, company_name: str) -> CompanyInsights:
        """
        Search web for company information using FireCrawl

        Args:
            company_name: Company to search for

        Returns:
            CompanyInsights object with web research data
        """
        print(f"   🔥 Searching web for '{company_name}'...")

        highlights = []
        news_items = []
        culture_notes = []
        sentiment_scores = []

        try:
            # Search queries for company information - FOCUSED on tech companies and careers
            # Reduced to 3 queries to avoid rate limits
            search_queries = [
                f"{company_name} glassdoor employee reviews interview",
                f"{company_name} reddit software engineer culture",
                f"{company_name} crunchbase funding news"
            ]

            print(f"   🔎 Searching {len(search_queries)} topics...")

            for query in search_queries:
                try:
                    # Use FireCrawl search API
                    search_results = self.firecrawl.search(
                        query=query,
                        limit=5  # Get top 5 results per query
                    )

                    # Extract web results
                    web_results = search_results.web if hasattr(search_results, 'web') and search_results.web else []

                    for result in web_results:
                        # Extract info from result
                        title = result.title if hasattr(result, 'title') else ""
                        description = result.description if hasattr(result, 'description') else ""
                        url = result.url if hasattr(result, 'url') else ""

                        # Combine title and description
                        text = f"{title}\n{description}"

                        # Skip if too short
                        if len(text) < 30:
                            continue

                        # Check if company name appears in the text
                        text_lower = text.lower()
                        company_lower = company_name.lower()

                        if company_lower not in text_lower:
                            continue

                        # IMPORTANT: Filter out irrelevant results
                        # Skip social media spam, shopping sites, etc.
                        irrelevant_keywords = [
                            "instagram", "facebook", "tiktok", "buy now", "shop",
                            "discount", "sale", "price", "shipping", "cart",
                            "cryptocurrency", "bitcoin", "forex", "trading signals"
                        ]
                        if any(keyword in text_lower for keyword in irrelevant_keywords):
                            continue

                        # Skip if URL is from irrelevant domains
                        irrelevant_domains = [
                            "instagram.com", "facebook.com", "tiktok.com",
                            "amazon.com", "ebay.com", "aliexpress.com",
                            "shopify.com", "etsy.com"
                        ]
                        if any(domain in url.lower() for domain in irrelevant_domains):
                            continue

                        # PREFER results from career/tech sites
                        career_sites = [
                            "glassdoor", "linkedin", "indeed", "reddit",
                            "blind", "levels.fyi", "crunchbase", "techcrunch",
                            "ycombinator", "stackoverflow", "github"
                        ]
                        is_career_site = any(site in url.lower() or site in text_lower for site in career_sites)

                        # Skip non-career sites unless they have very relevant content
                        if not is_career_site:
                            # For non-career sites, require stricter relevance
                            required_keywords = ["interview", "work", "employee", "culture", "review", "salary", "career"]
                            if not any(keyword in text_lower for keyword in required_keywords):
                                continue

                        # Categorize the result
                        if "glassdoor" in query or "review" in query or "employee" in query or "culture" in query or "interview" in query or "reddit" in query:
                            highlights.append(text[:500])

                            # Simple sentiment analysis
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

                            # Extract culture notes
                            if any(word in text_lower for word in ["culture", "work-life", "remote", "benefits"]):
                                culture_notes.append(text[:200])

                        elif "news" in query or "funding" in query:
                            news_items.append(f"{title[:100]}")

                except Exception as e:
                    print(f"   ⚠️  Error searching '{query}': {e}")
                    continue

        except Exception as e:
            print(f"   ❌ FireCrawl search failed: {e}")
            return CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[f"No web information found for {company_name}"],
                recent_news=[],
                culture_notes=[],
                data_source="firecrawl_error"
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
        if not highlights and not news_items:
            print(f"   📝 No web information found for {company_name}")
            return CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[],
                recent_news=[],
                culture_notes=[],
                data_source="firecrawl"
            )

        print(f"   ✅ Found {len(highlights)} reviews, {len(news_items)} news items")

        return CompanyInsights(
            company_name=company_name,
            reddit_sentiment=sentiment,
            reddit_highlights=highlights[:10],  # Top 10 insights
            recent_news=news_items[:5],  # Top 5 news items
            culture_notes=culture_notes[:5],  # Top 5 culture notes
            data_source="firecrawl"
        )


    async def _generate_ai_insights(
        self,
        role: str,
        company_name: str,
        insights: CompanyInsights
    ) -> Optional[str]:
        """
        Generate AI-powered interview prep insights from FireCrawl data

        Args:
            role: The job role being applied for
            company_name: Name of the company
            insights: Raw CompanyInsights from FireCrawl

        Returns:
            AI-generated summary string, or None if OpenAI is not available
        """
        if not self.openai_client:
            return None

        # Check if there's data available
        has_web_data = insights.reddit_highlights and len(insights.reddit_highlights) > 0

        if not has_web_data and not insights.recent_news:
            print(f"   ⚠️  No data available for AI analysis")
            return None

        print(f"   🤖 Generating AI insights for {role} role at {company_name}...")

        # Build context from web data
        if has_web_data:
            web_context = "\n".join([
                f"- {highlight}" for highlight in insights.reddit_highlights[:10]
            ])
            culture_context = "\n".join([
                f"- {note}" for note in insights.culture_notes[:5]
            ]) if insights.culture_notes else "No specific culture notes available."
            news_context = "\n".join([
                f"- {news}" for news in insights.recent_news[:5]
            ]) if insights.recent_news else "No recent news available."
        else:
            web_context = "No web information found for this company."
            culture_context = "No culture notes available."
            news_context = "\n".join([
                f"- {news}" for news in insights.recent_news[:5]
            ]) if insights.recent_news else "No recent news available."

        # Create the prompt for OpenAI
        prompt = f"""You are an expert career coach preparing a candidate for a job interview.

Company: {company_name}
Role: {role}
Overall Sentiment: {insights.reddit_sentiment}

Web Research Findings:
{web_context}

Culture Notes:
{culture_context}

Recent News:
{news_context}

---

**YOUR CRITICAL TASK**: Create a comprehensive interview prep brief using ALL available information.

**SECTION 1: Company Overview (2-3 bullets)**
Based on the web research above:
- What does {company_name} do? (products, services, industry)
- What are their main business areas or key offerings?
- Any notable facts candidates should know?

**SECTION 2: Interview Insights (2-3 bullets)**
{"From web research:" if has_web_data else "General interview preparation tips:"}
- Interview process insights (what to expect, question types, difficulty)
- Company culture patterns (work environment, team dynamics, values)
- Technical stack and work practices relevant to {role}
- Red flags or positive signals

**FILTERING RULES:**
- IGNORE personal drama, toxic manager stories, incomplete posts
- IGNORE anything not useful for a {role} interview
- Be specific and actionable
{"- If NO web data available, provide general interview tips for the role" if not has_web_data else ""}

**OUTPUT FORMAT:**
Structure your response as:

**About {company_name}:**
• [What the company does - from web research]
• [Main products/services]
• [Key fact to know]

{"**Interview Prep:**" if has_web_data else "**General Interview Tips for " + role + ":**"}
• [Interview insight 1]
• [Interview insight 2]
• [Interview insight 3]

**GUIDELINES:**
- Each bullet: ONE clear insight, max 25 words
- Be specific and direct
- No fluff or filler
- Focus on what's available: {"web research insights" if has_web_data else "general interview tips"}

Write the structured brief now:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career coach who provides sharp, insightful interview prep advice based on company research."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            ai_summary = response.choices[0].message.content.strip()
            print(f"   ✅ AI insights generated ({len(ai_summary)} chars)")
            return ai_summary

        except Exception as e:
            print(f"   ⚠️  AI analysis failed: {e}")
            return None

    async def get_insights(
        self,
        company_name: str,
        role: Optional[str] = None
    ) -> CompanyInsights:
        """
        Main method: Get company insights with AI-powered analysis

        Args:
            company_name: Name of the company to research
            role: The job role being applied for (optional, enables AI analysis)

        Returns:
            CompanyInsights object with all gathered information and AI insights

        Example:
            agent = NewsAgent()
            insights = await agent.get_insights("Nvidia", role="Software Engineer")
        """
        print(f"🔍 Researching company: {company_name}")

        # Use FireCrawl with timeout protection
        import asyncio

        try:
            # Set timeout of 60 seconds for FireCrawl search to prevent hanging
            insights = await asyncio.wait_for(
                self._search_firecrawl(company_name),
                timeout=60.0
            )
            print(f"✅ Found insights for {company_name}!")
            print(f"   Sentiment: {insights.reddit_sentiment}")
            print(f"   Highlights: {len(insights.reddit_highlights)} items")
            print(f"   News: {len(insights.recent_news)} items")

        except asyncio.TimeoutError:
            print(f"   ⏱️  FireCrawl search timed out after 60s")
            print(f"   → Returning neutral insights")
            insights = CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[f"FireCrawl search timed out for {company_name}"],
                recent_news=[],
                culture_notes=[],
                data_source="timeout"
            )
        except Exception as e:
            print(f"   ❌ FireCrawl search failed: {str(e)}")
            print(f"   → Returning neutral insights")
            insights = CompanyInsights(
                company_name=company_name,
                reddit_sentiment="neutral",
                reddit_highlights=[f"No web information found for {company_name}"],
                recent_news=[],
                culture_notes=[],
                data_source="error"
            )

        # Generate AI insights if role is provided and OpenAI is available
        if role and self.openai_client:
            ai_summary = await self._generate_ai_insights(role, company_name, insights)
            if ai_summary:
                # Create new insights object with AI summary
                insights = CompanyInsights(
                    company_name=insights.company_name,
                    reddit_sentiment=insights.reddit_sentiment,
                    reddit_highlights=insights.reddit_highlights,
                    recent_news=insights.recent_news,
                    culture_notes=insights.culture_notes,
                    data_source=insights.data_source,
                    ai_summary=ai_summary
                )
                print(f"   🎯 AI analysis complete!\n")
            else:
                print(f"   ⚠️  Skipping AI analysis (no data or error)\n")
        elif role and not self.openai_client:
            print(f"   ⚠️  AI analysis requested but OpenAI not configured\n")
        else:
            print(f"   ℹ️  No role specified - skipping AI analysis\n")

        return insights


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio

    async def test():
        agent = NewsAgent()

        # Test with companies and job roles
        test_cases = [
            ("Nvidia", "Senior Software Engineer"),
            ("Playtika", "Backend Developer")
        ]

        print("🗞️  News & Forum Intelligence Agent Test (with AI Insights)")
        print("=" * 80)

        for company, role in test_cases:
            print(f"\n{'=' * 80}")
            print(f"Testing: {role} at {company}")
            print("=" * 80)

            # Get insights WITH AI analysis by providing role
            insights = await agent.get_insights(company, role=role)

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

            # Display the AI-generated insights
            if insights.ai_summary:
                print(f"\n   🤖 AI INTERVIEW PREP BRIEF:")
                print("   " + "-" * 76)
                # Indent each line of the AI summary
                for line in insights.ai_summary.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 76)

            print("\n" + "-" * 80)

        print("\n✅ Agent 3 Test Complete!")

    asyncio.run(test())



