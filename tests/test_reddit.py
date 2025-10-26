"""
Test Reddit API integration
"""
import asyncio
from agents.news_agent import NewsAgent


async def test_reddit():
    print("🧪 Testing Reddit API Integration\n")
    print("=" * 80)

    # Create agent with Reddit API (not mock!)
    agent = NewsAgent(use_mock=False)

    # Test with a well-known tech company
    companies = ["Google", "Microsoft"]

    for company in companies:
        print(f"\n🔍 Testing with: {company}")
        print("-" * 80)

        insights = await agent.get_insights(company)

        print(f"\n📊 Results:")
        print(f"   Company: {insights.company_name}")
        print(f"   Sentiment: {insights.reddit_sentiment}")
        print(f"   Data Source: {insights.data_source}")
        print(f"\n   💬 Highlights ({len(insights.reddit_highlights)}):")
        for i, highlight in enumerate(insights.reddit_highlights[:3], 1):
            print(f"      {i}. {highlight[:100]}...")

        print("\n" + "=" * 80)

    print("\n✅ Reddit API Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_reddit())
