"""
Quick test for News Agent
"""
import asyncio
from agents.news_agent import NewsAgent


async def main():
    print("🧪 Quick News Agent Test\n")

    # Create agent (uses Reddit API by default!)
    agent = NewsAgent()

    # Pick a company to research
    company = input("Enter company name (or press Enter for 'Google'): ").strip()
    if not company:
        company = "Google"

    print(f"\n🔍 Researching: {company}\n")
    print("=" * 60)

    # Get insights
    insights = await agent.get_insights(company)

    # Display results
    print(f"\n📊 Results for: {insights.company_name}")
    print(f"   Sentiment: {insights.reddit_sentiment}")
    print(f"   Data Source: {insights.data_source}")

    print(f"\n   💬 Reddit Highlights:")
    for i, highlight in enumerate(insights.reddit_highlights, 1):
        print(f"      {i}. {highlight[:150]}...")

    if insights.recent_news:
        print(f"\n   📰 Recent News:")
        for news in insights.recent_news:
            print(f"      • {news}")

    if insights.culture_notes:
        print(f"\n   🏢 Culture Notes:")
        for note in insights.culture_notes:
            print(f"      • {note[:100]}...")

    print("\n" + "=" * 60)
    print("✅ Test Complete!")


if __name__ == "__main__":
    asyncio.run(main())
