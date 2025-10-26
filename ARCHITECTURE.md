# 🏗️ Architecture - job-finder

**תאריך:** 21 אוקטובר 2025
**גרסה:** 1.0

---

## 🎯 מטרת הפרויקט

מערכת **multi-agent** פשוטה וברורה למציאת משרות, שמשלבת:
- ניתוח קורות חיים חכם
- חיפוש משרות בזמן אמת
- מידע על חברות מפורומים (Reddit) וחדשות
- התאמה חכמה בין המשרות לקורות החיים

**העיקרון:** כל agent עושה דבר אחד טוב, ה-pipeline מחבר אותם.

---

## 🤖 4 Agents - תיאור מפורט

### Agent 1: CV Analyzer 📄

**תפקיד:** מנתח קורות חיים ומוציא מידע מובנה

**Input:**
- קובץ PDF/Text של קורות חיים

**Process:**
1. קריאת הקובץ (PyPDF2)
2. ניקוי טקסט (regex, NLP)
3. שליחה ל-OpenAI לזיהוי:
   - Skills (Python, Docker, AWS, etc.)
   - Experience level (Junior/Mid/Senior/Lead)
   - Preferred locations
   - Years of experience

**Output (Pydantic model):**
```python
class CVAnalysis(BaseModel):
    skills: List[str]
    experience_level: Literal["Junior", "Mid", "Senior", "Lead"]
    years_of_experience: int
    preferred_locations: List[str]
    key_achievements: List[str]
```

**Files:**
- `agents/cv_analyzer.py`
- `tests/test_cv_analyzer.py`

---

### Agent 2: Job Scraper 🔍

**תפקיד:** מחפש משרות מאתרי דרושים

**Input:**
- Job title (e.g., "Python Developer")
- Location (optional)
- Number of jobs to fetch (default: 20)

**Process:**
1. Scraping מ-LinkedIn Jobs / Indeed (BeautifulSoup)
2. Parsing של:
   - Job title
   - Company name
   - Location
   - Job description
   - Application URL
3. ניקוי ונרמול של הנתונים

**Output (Pydantic model):**
```python
class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str]
    source: Literal["linkedin", "indeed", "direct"]
```

**Files:**
- `agents/job_scraper.py`
- `tests/test_job_scraper.py`

---

### Agent 3: News & Forum Intelligence 📰

**תפקיד:** אוסף מידע על חברות מפורומים וחדשות

**Input:**
- Company name

**Process:**
1. **Reddit scraping:**
   - חיפוש בsubreddits רלוונטיים (/r/cscareerquestions, /r/experienceddevs)
   - איסוף posts על החברה
   - Sentiment analysis (חיובי/שלילי)

2. **News scraping:**
   - חדשות עדכניות על החברה
   - מימון, צמיחה, שינויים ניהוליים

**Output (Pydantic model):**
```python
class CompanyInsights(BaseModel):
    company_name: str
    reddit_sentiment: Literal["positive", "neutral", "negative"]
    reddit_highlights: List[str]  # 3-5 insights מרדיט
    recent_news: List[str]  # 3-5 כותרות חדשות
    culture_notes: List[str]  # תרבות ארגונית
    data_source: str
```

**Files:**
- `agents/news_agent.py`
- `tests/test_news_agent.py`

---

### Agent 4: Smart Matcher 🎯

**תפקיד:** משווה CV למשרות ונותן ציון התאמה

**Input:**
- CV Analysis
- List of Jobs
- Company Insights (per job)

**Process:**
1. **Embeddings:**
   - יצירת embedding ל-CV (OpenAI)
   - יצירת embedding לכל job description

2. **Similarity calculation:**
   - Cosine similarity בין CV לjob
   - בדיקת skill overlap
   - התאמת experience level

3. **Scoring:**
   - ציון בסיס (0-100) לפי similarity
   - בונוס/עונש לפי company insights
   - Ranking של כל המשרות

**Output (Pydantic model):**
```python
class JobMatch(BaseModel):
    job: Job
    company_insights: CompanyInsights
    match_score: float  # 0-100
    skill_overlap: List[str]
    skill_gaps: List[str]
    recommendation: str  # "Strong Match", "Good Fit", "Consider", "Skip"
    reasoning: List[str]  # למה זה התאמה טובה/לא טובה
```

**Files:**
- `agents/matcher.py`
- `tests/test_matcher.py`

---

## 🔄 Pipeline Architecture

### Stage-Based Execution

```
┌─────────────────────────────────────────────────┐
│ Stage 1: Input Processing (Parallel)           │
├─────────────────────────────────────────────────┤
│  Task 1.1: CV Analysis     → CV Analyzer       │
│  Task 1.2: Job Search      → Job Scraper       │
│                                                 │
│  ⏱️ Duration: ~5-10 seconds                     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Stage 2: Enrichment (Parallel per Job)         │
├─────────────────────────────────────────────────┤
│  For each job in Jobs:                          │
│    Task 2.1: Get Company Insights → News Agent │
│                                                 │
│  ⏱️ Duration: ~2-3 seconds per job (parallel)   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Stage 3: Matching (Sequential)                 │
├─────────────────────────────────────────────────┤
│  Task 3.1: Match & Rank → Smart Matcher        │
│                                                 │
│  ⏱️ Duration: ~3-5 seconds                      │
└─────────────────────────────────────────────────┘
                    ↓
                 Results!
```

### Pipeline Implementation

**File: `pipeline/orchestrator.py`**

```python
class JobFinderPipeline:
    """Main pipeline orchestrator"""

    async def run(self, cv_path: str, job_title: str, num_jobs: int = 20):
        # Stage 1: Parallel input processing
        cv_analysis, jobs = await asyncio.gather(
            self.cv_analyzer.analyze(cv_path),
            self.job_scraper.search(job_title, num_jobs)
        )

        # Stage 2: Parallel company insights (per job)
        insights_tasks = [
            self.news_agent.get_insights(job.company)
            for job in jobs
        ]
        all_insights = await asyncio.gather(*insights_tasks)

        # Stage 3: Matching & ranking
        matches = await self.matcher.match_and_rank(
            cv_analysis, jobs, all_insights
        )

        return matches
```

**למה זה יעיל:**
- ✅ Stage 1 רץ במקביל - חוסך זמן!
- ✅ Stage 2 רץ במקביל על כל המשרות
- ✅ Stage 3 מקבל הכל מוכן ועושה ranking מהיר

---

## 📊 Data Flow

```
CV (PDF)
   ↓
[CV Analyzer] → CVAnalysis
                      ↓
                      ↓ ← [Job Scraper] → List[Job]
                      ↓         ↓
                      ↓    [News Agent] → List[CompanyInsights]
                      ↓         ↓
                      ↓─────────↓
                           ↓
                    [Smart Matcher]
                           ↓
                    List[JobMatch]
                    (sorted by score)
```

---

## 🗂️ Models (Pydantic)

**File: `models/models.py`**

כל המודלים יהיו ב-Pydantic v2 עם validation:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class CVAnalysis(BaseModel):
    """Output של CV Analyzer"""
    skills: List[str]
    experience_level: Literal["Junior", "Mid", "Senior", "Lead"]
    years_of_experience: int = Field(ge=0, le=50)
    preferred_locations: List[str] = Field(default_factory=list)
    key_achievements: List[str] = Field(default_factory=list)

class Job(BaseModel):
    """משרה בודדת"""
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str] = None
    source: Literal["linkedin", "indeed", "direct"] = "direct"

class CompanyInsights(BaseModel):
    """תובנות על חברה"""
    company_name: str
    reddit_sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    reddit_highlights: List[str] = Field(default_factory=list)
    recent_news: List[str] = Field(default_factory=list)
    culture_notes: List[str] = Field(default_factory=list)
    data_source: str = "multiple"

class JobMatch(BaseModel):
    """משרה מותאמת עם ציון"""
    job: Job
    company_insights: CompanyInsights
    match_score: float = Field(ge=0, le=100)
    skill_overlap: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    recommendation: Literal["Strong Match", "Good Fit", "Consider", "Skip"] = "Consider"
    reasoning: List[str] = Field(default_factory=list)
```

---

## 🧪 Testing Strategy

### Unit Tests (per agent)
- `test_cv_analyzer.py` - בדיקת parsing, OpenAI integration
- `test_job_scraper.py` - בדיקת scraping, error handling
- `test_news_agent.py` - בדיקת Reddit API, sentiment analysis
- `test_matcher.py` - בדיקת scoring logic

### Integration Tests
- `test_pipeline.py` - end-to-end pipeline test

### מה נבדוק:
- ✅ Valid inputs → valid outputs
- ✅ Invalid inputs → proper errors
- ✅ Edge cases (empty CV, no jobs found, etc.)
- ✅ Mocking של API calls (OpenAI, Reddit)

---

## 🔐 Environment Variables

**File: `.env.example`**

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Reddit API (create app at reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=job-finder/1.0

# Optional: News API
NEWS_API_KEY=your-news-api-key
```

---

## 📦 Dependencies

**File: `requirements.txt`**

```
# Core
pydantic>=2.7.0
python-dotenv>=1.0.0

# PDF Processing
PyPDF2>=3.0.0

# Web Scraping
beautifulsoup4>=4.12.0
requests>=2.31.0
selenium>=4.0.0  # If needed for dynamic content

# Reddit
praw>=7.7.0

# OpenAI
openai>=1.40.0

# Async
aiohttp>=3.9.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0

# Utilities
numpy>=1.26.0
scikit-learn>=1.4.0  # For cosine similarity
```

---

## 🚀 Usage Example

```python
from pipeline.orchestrator import JobFinderPipeline

# Initialize pipeline
pipeline = JobFinderPipeline()

# Run
matches = await pipeline.run(
    cv_path="examples/my_cv.pdf",
    job_title="Python Developer",
    num_jobs=20
)

# Print top 5 matches
for match in matches[:5]:
    print(f"{match.job.title} at {match.job.company}")
    print(f"Score: {match.match_score}/100")
    print(f"Recommendation: {match.recommendation}")
    print(f"Reasoning: {', '.join(match.reasoning)}")
    print("---")
```

---

## 📈 Future Improvements (V2)

אם נרצה להרחיב בעתיד:
- 🔄 Celery/Redis לqueue של tasks
- 💾 Database (PostgreSQL) לשמירת results
- 🌐 FastAPI endpoint ל-REST API
- 📧 Email notifications
- 📊 Dashboard (Streamlit)
- 🤖 More agents (Salary predictor, Interview prep)

**אבל לא עכשיו! V1 = פשוט ועובד.**

---

## 🎓 Learning Goals

מה אתה תלמד בפרויקט הזה:
- ✅ Multi-agent architecture
- ✅ Async/await programming
- ✅ Pydantic models & validation
- ✅ Web scraping (BeautifulSoup)
- ✅ Reddit API (PRAW)
- ✅ OpenAI API (embeddings, chat)
- ✅ Testing best practices
- ✅ Clean code structure

**זה הפרויקט שתראה ל-recruiters!** 🎯

---

**עדכון אחרון:** 21 אוקטובר 2025
