"""
Unit tests for News Agent
Tests Reddit integration, company research, AI insights, and edge cases
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from typing import List

from agents.news_agent import NewsAgent
from models.models import CompanyInsights


class TestNewsAgentInitialization:
    """Test NewsAgent initialization with different configurations"""

    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "OPENAI_API_KEY": "test_openai_key",
        "BRAVE_SEARCH_API_KEY": "test_brave_key"
    })
    @patch('agents.news_agent.OpenAI')
    def test_init_with_all_credentials(self, mock_openai):
        """Test successful initialization with all credentials"""
        with patch('agents.brave_search.BraveSearchAgent'):
            agent = NewsAgent()

            assert agent.reddit_client_id == "test_client_id"
            assert agent.reddit_client_secret == "test_secret"
            assert agent.reddit_user_agent == "test_agent"
            assert agent.openai_client is not None
            assert agent.use_brave_search is True

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_reddit_credentials_raises_error(self):
        """Test that missing Reddit credentials raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            NewsAgent()
        assert "Reddit API credentials not found" in str(excinfo.value)

    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "",
        "REDDIT_USER_AGENT": "test_agent"
    })
    def test_init_with_empty_reddit_secret_raises_error(self):
        """Test that empty Reddit secret raises ValueError"""
        with pytest.raises(ValueError) as excinfo:
            NewsAgent()
        assert "Reddit API credentials not found" in str(excinfo.value)

    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent"
        # No OPENAI_API_KEY
    }, clear=True)
    def test_init_without_openai_key_disables_ai(self):
        """Test initialization without OpenAI disables AI features"""
        with patch('agents.brave_search.BraveSearchAgent', side_effect=Exception("No key")):
            agent = NewsAgent()

            assert agent.openai_client is None
            assert agent.reddit_client_id == "test_client_id"

    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "OPENAI_API_KEY": "test_openai_key"
        # No BRAVE_SEARCH_API_KEY
    })
    @patch('agents.news_agent.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent', side_effect=Exception("No Brave API key"))
    def test_init_without_brave_search_disables_search(self, mock_brave, mock_openai):
        """Test initialization without Brave Search disables company research"""
        agent = NewsAgent()

        assert agent.use_brave_search is False
        assert agent.openai_client is not None


class TestGetMockInsights:
    """Test mock insights generation for known companies"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test agent"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_secret",
            "REDDIT_USER_AGENT": "test_agent"
        }), patch('agents.brave_search.BraveSearchAgent'):
            self.agent = NewsAgent()
            yield

    def test_mock_insights_for_known_company(self):
        """Test getting mock insights for a known company"""
        insights = self.agent._get_mock_insights("TechCorp Israel")

        assert insights.company_name == "TechCorp Israel"
        assert insights.reddit_sentiment == "positive"
        assert len(insights.reddit_highlights) > 0
        assert len(insights.recent_news) > 0
        assert insights.data_source == "mock_data"

    def test_mock_insights_for_startupxyz(self):
        """Test mock insights for StartupXYZ"""
        insights = self.agent._get_mock_insights("StartupXYZ")

        assert insights.company_name == "StartupXYZ"
        assert insights.reddit_sentiment == "positive"
        assert "Fast-paced startup environment" in insights.reddit_highlights
        assert any("equity" in h.lower() for h in insights.reddit_highlights)

    def test_mock_insights_for_unknown_company(self):
        """Test getting mock insights for an unknown company"""
        insights = self.agent._get_mock_insights("UnknownCompany123")

        assert insights.company_name == "UnknownCompany123"
        assert insights.reddit_sentiment == "neutral"
        assert "Limited public information" in insights.reddit_highlights[0]
        assert insights.data_source == "mock_data"

    def test_mock_insights_for_ai_innovations(self):
        """Test mock insights for AI Innovations company"""
        insights = self.agent._get_mock_insights("AI Innovations")

        assert insights.company_name == "AI Innovations"
        assert insights.reddit_sentiment == "positive"
        assert any("AI" in h or "LLM" in h for h in insights.reddit_highlights)
        assert len(insights.culture_notes) > 0

    def test_mock_insights_for_fintech_solutions(self):
        """Test mock insights for FinTech Solutions"""
        insights = self.agent._get_mock_insights("FinTech Solutions")

        assert insights.company_name == "FinTech Solutions"
        assert insights.reddit_sentiment == "positive"
        assert any("stable" in h.lower() for h in insights.reddit_highlights)

    def test_mock_insights_structure_completeness(self):
        """Test that all mock insights have complete structure"""
        companies = ["TechCorp Israel", "StartupXYZ", "DataScience Ltd",
                    "FinTech Solutions", "AI Innovations", "CloudTech"]

        for company in companies:
            insights = self.agent._get_mock_insights(company)

            assert insights.company_name == company
            assert insights.reddit_sentiment in ["positive", "neutral", "negative"]
            assert isinstance(insights.reddit_highlights, list)
            assert isinstance(insights.recent_news, list)
            assert isinstance(insights.culture_notes, list)
            assert insights.data_source == "mock_data"


class TestSearchRedditPRAW:
    """Test Reddit search functionality using PRAW"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent"
    })
    @patch('agents.brave_search.BraveSearchAgent')
    def agent(self, mock_brave):
        """Create test agent"""
        return NewsAgent()

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_success(self, mock_praw, agent):
        """Test successful Reddit search with relevant posts"""
        # Mock Reddit client
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        # Mock subreddit and search results
        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create mock submissions
        mock_submission1 = MagicMock()
        mock_submission1.title = "Google is a great place to work"
        mock_submission1.selftext = "I've been working at Google for 2 years and love the culture. Great work-life balance."

        mock_submission2 = MagicMock()
        mock_submission2.title = "Google interview experience"
        mock_submission2.selftext = "Just finished interviews at Google. Amazing team and interesting technical questions."

        mock_subreddit.search.return_value = [mock_submission1, mock_submission2]

        # Test the search
        insights = await agent._search_reddit_praw("Google")

        assert insights.company_name == "Google"
        assert len(insights.reddit_highlights) > 0
        assert insights.data_source == "reddit_praw"

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_no_results(self, mock_praw, agent):
        """Test Reddit search with no relevant results"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_subreddit.search.return_value = []

        insights = await agent._search_reddit_praw("ObscureCompany999")

        assert insights.company_name == "ObscureCompany999"
        assert insights.reddit_sentiment == "neutral"
        assert len(insights.reddit_highlights) == 0

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_connection_failure(self, mock_praw, agent):
        """Test handling of Reddit connection failure"""
        mock_praw.side_effect = Exception("Connection failed")

        insights = await agent._search_reddit_praw("TestCompany")

        assert insights.company_name == "TestCompany"
        assert insights.reddit_sentiment == "neutral"
        assert insights.data_source == "reddit_praw"

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_sentiment_analysis_positive(self, mock_praw, agent):
        """Test sentiment analysis extracts positive sentiment"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create positive posts
        positive_posts = []
        for i in range(5):
            mock_post = MagicMock()
            mock_post.title = f"Microsoft is great and amazing. Best company ever!"
            mock_post.selftext = "I love working here. Excellent culture and great benefits."
            positive_posts.append(mock_post)

        mock_subreddit.search.return_value = positive_posts

        insights = await agent._search_reddit_praw("Microsoft")

        # Should detect positive sentiment
        assert insights.reddit_sentiment == "positive"

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_sentiment_analysis_negative(self, mock_praw, agent):
        """Test sentiment analysis extracts negative sentiment"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create negative posts
        negative_posts = []
        for i in range(5):
            mock_post = MagicMock()
            mock_post.title = f"BadCorp is terrible. Worst place to work."
            mock_post.selftext = "Avoid this company. Toxic culture and horrible management."
            negative_posts.append(mock_post)

        mock_subreddit.search.return_value = negative_posts

        insights = await agent._search_reddit_praw("BadCorp")

        # Should detect negative sentiment
        assert insights.reddit_sentiment == "negative"

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_search_reddit_filters_irrelevant_posts(self, mock_praw, agent):
        """Test that irrelevant posts are filtered out"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create posts where company name doesn't appear
        irrelevant_posts = []
        for i in range(5):
            mock_post = MagicMock()
            mock_post.title = "Some random tech discussion"
            mock_post.selftext = "No mention of the company here at all"
            irrelevant_posts.append(mock_post)

        mock_subreddit.search.return_value = irrelevant_posts

        insights = await agent._search_reddit_praw("SpecificCompany")

        # Should return empty results since posts don't mention company
        assert len(insights.reddit_highlights) == 0


class TestResearchCompanyBackground:
    """Test company research using Brave Search"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "BRAVE_SEARCH_API_KEY": "test_brave_key"
    })
    @patch('agents.brave_search.BraveSearchAgent')
    def agent_with_brave(self, mock_brave_cls):
        """Create test agent with Brave Search enabled"""
        mock_brave_instance = MagicMock()
        mock_brave_cls.return_value = mock_brave_instance

        agent = NewsAgent()
        agent.brave_agent = mock_brave_instance
        agent.use_brave_search = True
        return agent

    @pytest.mark.asyncio
    async def test_research_company_background_success(self, agent_with_brave):
        """Test successful company background research"""
        # Mock Brave Search results
        mock_results = [
            {
                "title": "Apple Inc. - Technology Company",
                "description": "Apple designs and manufactures consumer electronics, software, and online services."
            },
            {
                "title": "Apple Career Opportunities",
                "description": "Join Apple and work on innovative products used by millions worldwide."
            }
        ]

        agent_with_brave.brave_agent.search_company_info = AsyncMock(return_value=mock_results)

        background = await agent_with_brave._research_company_background("Apple")

        assert background is not None
        assert "Apple" in background
        assert "Technology Company" in background

    @pytest.mark.asyncio
    async def test_research_company_background_no_results(self, agent_with_brave):
        """Test company research with no results"""
        agent_with_brave.brave_agent.search_company_info = AsyncMock(return_value=[])

        background = await agent_with_brave._research_company_background("UnknownCorp")

        assert background is None

    @pytest.mark.asyncio
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent"
    })
    @patch('agents.brave_search.BraveSearchAgent')
    async def test_research_company_background_brave_disabled(self, mock_brave):
        """Test company research when Brave Search is disabled"""
        agent = NewsAgent()
        agent.use_brave_search = False

        background = await agent._research_company_background("TestCorp")

        assert background is None


class TestGenerateAIInsights:
    """Test AI-powered insights generation"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "OPENAI_API_KEY": "test_openai_key"
    })
    @patch('agents.news_agent.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def agent_with_openai(self, mock_brave, mock_openai_cls):
        """Create test agent with OpenAI enabled"""
        mock_openai_instance = MagicMock()
        mock_openai_cls.return_value = mock_openai_instance

        agent = NewsAgent()
        agent.openai_client = mock_openai_instance
        agent.use_brave_search = False  # Disable Brave for simpler tests
        return agent

    @pytest.mark.asyncio
    async def test_generate_ai_insights_success(self, agent_with_openai):
        """Test successful AI insights generation"""
        # Mock CompanyInsights
        insights = CompanyInsights(
            company_name="Google",
            reddit_sentiment="positive",
            reddit_highlights=[
                "Great work-life balance",
                "Excellent benefits and perks",
                "Challenging technical problems"
            ],
            recent_news=["Google launches new AI product"],
            culture_notes=["Innovative culture", "Focus on research"],
            data_source="reddit_praw"
        )

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
**About Google:**
• Leading tech company specializing in search, cloud, and AI
• Known for innovative products used by billions worldwide
• Strong focus on research and development

**Interview Prep:**
• Expect algorithmic and system design questions
• Culture values innovation and collaborative problem-solving
• Benefits package is highly competitive
"""

        agent_with_openai.openai_client.chat.completions.create.return_value = mock_response

        ai_summary = await agent_with_openai._generate_ai_insights(
            role="Software Engineer",
            company_name="Google",
            insights=insights
        )

        assert ai_summary is not None
        assert "Google" in ai_summary
        assert "Interview Prep" in ai_summary

    @pytest.mark.asyncio
    async def test_generate_ai_insights_no_openai_client(self):
        """Test AI insights when OpenAI is not available"""
        with patch.dict(os.environ, {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_secret",
            "REDDIT_USER_AGENT": "test_agent"
        }), patch('agents.brave_search.BraveSearchAgent'):
            agent = NewsAgent()
            agent.openai_client = None

            insights = CompanyInsights(
                company_name="TestCorp",
                reddit_sentiment="neutral",
                reddit_highlights=["Some info"],
                recent_news=[],
                culture_notes=[],
                data_source="reddit_praw"
            )

            ai_summary = await agent._generate_ai_insights(
                role="Developer",
                company_name="TestCorp",
                insights=insights
            )

            assert ai_summary is None

    @pytest.mark.asyncio
    async def test_generate_ai_insights_no_data(self, agent_with_openai):
        """Test AI insights when there's no data available"""
        insights = CompanyInsights(
            company_name="NoDataCorp",
            reddit_sentiment="neutral",
            reddit_highlights=[],  # No Reddit data
            recent_news=[],
            culture_notes=[],
            data_source="reddit_praw"
        )

        agent_with_openai.use_brave_search = False  # No Brave data either

        ai_summary = await agent_with_openai._generate_ai_insights(
            role="Engineer",
            company_name="NoDataCorp",
            insights=insights
        )

        # Should return None when no data available
        assert ai_summary is None

    @pytest.mark.asyncio
    async def test_generate_ai_insights_openai_error(self, agent_with_openai):
        """Test handling of OpenAI API errors"""
        insights = CompanyInsights(
            company_name="TestCorp",
            reddit_sentiment="positive",
            reddit_highlights=["Good company"],
            recent_news=[],
            culture_notes=[],
            data_source="reddit_praw"
        )

        # Mock OpenAI error
        agent_with_openai.openai_client.chat.completions.create.side_effect = Exception("API Error")

        ai_summary = await agent_with_openai._generate_ai_insights(
            role="Developer",
            company_name="TestCorp",
            insights=insights
        )

        assert ai_summary is None


class TestGetInsightsMainMethod:
    """Test the main get_insights method"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent",
        "OPENAI_API_KEY": "test_openai_key"
    })
    @patch('agents.news_agent.OpenAI')
    @patch('agents.brave_search.BraveSearchAgent')
    def agent(self, mock_brave, mock_openai):
        """Create test agent"""
        return NewsAgent()

    @pytest.mark.asyncio
    async def test_get_insights_full_workflow(self, agent):
        """Test complete workflow of getting insights"""
        # Mock _search_reddit_praw
        mock_insights = CompanyInsights(
            company_name="Microsoft",
            reddit_sentiment="positive",
            reddit_highlights=["Great benefits", "Good culture"],
            recent_news=["Microsoft expands cloud services"],
            culture_notes=["Collaborative environment"],
            data_source="reddit_praw"
        )

        agent._search_reddit_praw = AsyncMock(return_value=mock_insights)
        agent.openai_client = None  # Disable AI for this test

        insights = await agent.get_insights("Microsoft")

        assert insights.company_name == "Microsoft"
        assert insights.reddit_sentiment == "positive"
        assert len(insights.reddit_highlights) > 0

    @pytest.mark.asyncio
    async def test_get_insights_with_role_triggers_ai(self, agent):
        """Test that providing role triggers AI analysis"""
        mock_reddit_insights = CompanyInsights(
            company_name="Amazon",
            reddit_sentiment="positive",
            reddit_highlights=["Fast-paced environment"],
            recent_news=[],
            culture_notes=[],
            data_source="reddit_praw"
        )

        agent._search_reddit_praw = AsyncMock(return_value=mock_reddit_insights)
        agent._generate_ai_insights = AsyncMock(return_value="AI generated summary")

        insights = await agent.get_insights("Amazon", role="Backend Developer")

        # Verify AI insights were generated
        agent._generate_ai_insights.assert_called_once()
        assert insights.ai_summary == "AI generated summary"

    @pytest.mark.asyncio
    async def test_get_insights_timeout_handling(self, agent):
        """Test handling of Reddit search timeout"""
        # Mock timeout
        agent._search_reddit_praw = AsyncMock(side_effect=asyncio.TimeoutError())
        agent.openai_client = None

        insights = await agent.get_insights("TimeoutCorp")

        assert insights.company_name == "TimeoutCorp"
        assert insights.reddit_sentiment == "neutral"
        assert "timed out" in insights.reddit_highlights[0]
        assert insights.data_source == "timeout"

    @pytest.mark.asyncio
    async def test_get_insights_error_handling(self, agent):
        """Test handling of Reddit search errors"""
        agent._search_reddit_praw = AsyncMock(side_effect=Exception("API Error"))
        agent.openai_client = None

        insights = await agent.get_insights("ErrorCorp")

        assert insights.company_name == "ErrorCorp"
        assert insights.reddit_sentiment == "neutral"
        assert insights.data_source == "error"


class TestDifferentCompanyScenarios:
    """Test different types of companies to ensure comprehensive coverage"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent"
    })
    @patch('agents.brave_search.BraveSearchAgent')
    def agent(self, mock_brave):
        """Create test agent"""
        return NewsAgent()

    def test_large_tech_company_insights(self, agent):
        """Test insights for large tech companies"""
        companies = ["TechCorp Israel", "AI Innovations"]

        for company in companies:
            insights = agent._get_mock_insights(company)

            assert insights.reddit_sentiment in ["positive", "neutral", "negative"]
            assert len(insights.reddit_highlights) >= 3
            assert len(insights.recent_news) >= 1
            assert insights.company_name == company

    def test_startup_company_insights(self, agent):
        """Test insights for startup companies"""
        insights = agent._get_mock_insights("StartupXYZ")

        assert insights.company_name == "StartupXYZ"
        assert insights.reddit_sentiment == "positive"
        assert any("startup" in h.lower() for h in insights.reddit_highlights)
        assert any("equity" in h.lower() for h in insights.reddit_highlights)

    def test_enterprise_company_insights(self, agent):
        """Test insights for enterprise companies"""
        insights = agent._get_mock_insights("FinTech Solutions")

        assert insights.company_name == "FinTech Solutions"
        assert any("stable" in h.lower() or "benefits" in h.lower()
                  for h in insights.reddit_highlights)

    def test_neutral_sentiment_company(self, agent):
        """Test insights for companies with neutral sentiment"""
        insights = agent._get_mock_insights("DataScience Ltd")

        assert insights.reddit_sentiment == "neutral"
        assert len(insights.reddit_highlights) > 0

    def test_cloud_infrastructure_company(self, agent):
        """Test insights for cloud/infrastructure companies"""
        insights = agent._get_mock_insights("CloudTech")

        assert insights.company_name == "CloudTech"
        assert any("cloud" in h.lower() or "devops" in h.lower()
                  for h in insights.reddit_highlights)

    def test_multiple_companies_consistency(self, agent):
        """Test that insights are consistent across multiple calls"""
        company = "TechCorp Israel"

        insights1 = agent._get_mock_insights(company)
        insights2 = agent._get_mock_insights(company)

        # Should return identical results
        assert insights1.company_name == insights2.company_name
        assert insights1.reddit_sentiment == insights2.reddit_sentiment
        assert insights1.reddit_highlights == insights2.reddit_highlights

    def test_company_name_variations(self, agent):
        """Test handling of company name variations"""
        companies = [
            "TechCorp Israel",
            "AI Innovations",
            "FinTech Solutions",
            "UnknownCompany999"
        ]

        for company in companies:
            insights = agent._get_mock_insights(company)

            # Every company should get valid insights
            assert insights is not None
            assert insights.company_name == company
            assert isinstance(insights.reddit_highlights, list)
            assert isinstance(insights.recent_news, list)


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    @patch.dict(os.environ, {
        "REDDIT_CLIENT_ID": "test_client_id",
        "REDDIT_CLIENT_SECRET": "test_secret",
        "REDDIT_USER_AGENT": "test_agent"
    })
    @patch('agents.brave_search.BraveSearchAgent')
    def agent(self, mock_brave):
        """Create test agent"""
        return NewsAgent()

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_empty_company_name(self, mock_praw, agent):
        """Test handling of empty company name"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_subreddit.search.return_value = []

        insights = await agent._search_reddit_praw("")

        assert insights.company_name == ""
        assert insights.reddit_sentiment == "neutral"

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_special_characters_in_company_name(self, mock_praw, agent):
        """Test handling of special characters in company name"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_subreddit.search.return_value = []

        insights = await agent._search_reddit_praw("Company & Co. Inc.")

        assert insights.company_name == "Company & Co. Inc."

    @pytest.mark.asyncio
    @patch('praw.Reddit')
    async def test_very_long_company_name(self, mock_praw, agent):
        """Test handling of very long company name"""
        mock_reddit = MagicMock()
        mock_praw.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_subreddit.search.return_value = []

        long_name = "A" * 200  # Very long name
        insights = await agent._search_reddit_praw(long_name)

        assert insights.company_name == long_name

    def test_mock_insights_handles_all_data_types(self, agent):
        """Test that mock insights properly handles all data types"""
        insights = agent._get_mock_insights("TechCorp Israel")

        # Verify all fields are correct types
        assert isinstance(insights.company_name, str)
        assert isinstance(insights.reddit_sentiment, str)
        assert isinstance(insights.reddit_highlights, list)
        assert isinstance(insights.recent_news, list)
        assert isinstance(insights.culture_notes, list)
        assert isinstance(insights.data_source, str)

        # Verify list contents are strings
        assert all(isinstance(h, str) for h in insights.reddit_highlights)
        assert all(isinstance(n, str) for n in insights.recent_news)
        assert all(isinstance(c, str) for c in insights.culture_notes)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])