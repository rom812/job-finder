# Job Finder - Complete Pipeline Architecture Documentation

## Executive Summary

Job Finder is an AI-powered job matching system that analyzes candidate CVs and finds the most suitable job opportunities. It uses a **4-agent pipeline** orchestrated by an async coordinator that runs stages in parallel for optimal performance. The system combines CV analysis, intelligent job searching, company research, and semantic matching using OpenAI APIs.

**Key Features:**
- Multi-source job aggregation (JSearch API + Brave Search)
- AI-powered CV analysis and semantic matching
- Real-time company insights from Reddit and web research
- Smart ranking algorithm with skill overlap detection
- Async/parallel execution for performance

---

## Table of Contents

1. [Pipeline Flow Overview](#1-pipeline-flow-overview)
2. [Stage 1: Analysis & Discovery (Parallel)](#2-stage-1-analysis--discovery-parallel)
3. [Stage 2: Company Intelligence (Parallel)](#3-stage-2-company-intelligence-parallel)
4. [Stage 3: Matching & Ranking (Sequential)](#4-stage-3-matching--ranking-sequential)
5. [Data Models](#5-data-models)
6. [API Layer](#6-api-layer)
7. [Agent Deep Dive](#7-agent-deep-dive)
8. [Technologies & Libraries](#8-technologies--libraries)
9. [Communication Between Agents](#9-communication-between-agents)
10. [Execution Timeline Example](#10-execution-timeline-example)
11. [Error Handling & Resilience](#11-error-handling--resilience)
12. [Environment Configuration](#12-environment-configuration)
13. [Frontend Integration](#13-frontend-integration)
14. [Performance & Cost Analysis](#14-performance--cost-analysis)

---

## 1. Pipeline Flow Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│  (Name, Email, CV PDF, Job Title, Location, Job Level)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (Flask)                        │
│              POST /api/run-pipeline                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              PIPELINE ORCHESTRATOR                          │
│            (pipeline/orchestrator.py)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐     ┌───────────────────┐
│   STAGE 1 (Parallel)                        │
├───────────────────┤     ├───────────────────┤
│  Agent 1:         │     │  Agent 2:         │
│  CV Analyzer      │     │  Job Scraper      │
│                   │     │                   │
│  Input: PDF       │     │  Input: Query     │
│  Output:          │     │  Output:          │
│  CVAnalysis       │     │  List[Job]        │
│                   │     │                   │
│  • Read PDF       │     │  • Expand query   │
│  • Extract text   │     │  • Search JSearch │
│  • OpenAI GPT-4o  │     │  • Search Brave   │
│  • Parse skills   │     │  • Deduplicate    │
└─────────┬─────────┘     └─────────┬─────────┘
          │                         │
          └───────────┬─────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   STAGE 2 (Parallel per job) │
        ├─────────────────────────────┤
        │  Agent 3: News Agent        │
        │                             │
        │  Input: List[Job]           │
        │  Output:                    │
        │  List[CompanyInsights]      │
        │                             │
        │  • Search Reddit (PRAW)     │
        │  • Sentiment analysis       │
        │  • Brave company research   │
        │  • OpenAI insights          │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │   STAGE 3 (Sequential)      │
        ├─────────────────────────────┤
        │  Agent 4: Smart Matcher     │
        │                             │
        │  Input: CVAnalysis, Jobs,   │
        │         CompanyInsights     │
        │  Output: List[JobMatch]     │
        │                             │
        │  • Create embeddings        │
        │  • Cosine similarity        │
        │  • Skill overlap            │
        │  • Apply bonuses/penalties  │
        │  • Rank by score            │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │    RANKED JOB MATCHES       │
        │    (Sorted by score)        │
        └─────────────────────────────┘
```

### Execution Flow

**Entry Point:** User submits form via React frontend

**Stages:**
1. **Stage 1 (Parallel):** CV Analysis + Job Search run simultaneously
2. **Stage 2 (Parallel):** Company insights gathered for all jobs in parallel
3. **Stage 3 (Sequential):** Jobs ranked by semantic match + skill overlap

**Output:** Ranked list of `JobMatch` objects with scores, recommendations, and insights

---

## 2. Stage 1: Analysis & Discovery (Parallel)

Two tasks run simultaneously using `asyncio.gather()` to minimize total execution time.

### Agent 1: CV Analyzer

**File:** `agents/cv_analyzer.py`

**Purpose:** Extract structured data from candidate CV

#### Process Flow

```
PDF File → PyPDF2 Reader → Text Extraction → Clean Text →
OpenAI GPT-4o-mini → JSON Response → CVAnalysis Object
```

#### Implementation Details

**1. PDF Reading**
```python
reader = PdfReader(file)
for page in reader.pages:
    text += page.extract_text()
```

**2. Text Cleaning**
- Remove multiple whitespaces: `re.sub(r'\s+', ' ', text)`
- Strip leading/trailing whitespace

**3. OpenAI Analysis**
- **Model:** `gpt-4o-mini`
- **Response format:** `{"type": "json_object"}`
- **Prompt:** Analyzes skills, experience level, years, locations, achievements
- **Timeout:** 120 seconds

**4. Structured Output**
```python
CVAnalysis(
    skills=["Python", "Docker", "AWS", ...],
    experience_level="Mid",
    years_of_experience=3,
    preferred_locations=["Tel Aviv", "Remote"],
    key_achievements=["Built microservices architecture", ...]
)
```

#### Technologies Used
- **PyPDF2:** PDF text extraction
- **OpenAI GPT-4o-mini:** Natural language processing
- **Pydantic v2:** Data validation

#### API Costs
- **1 API call per CV** (~$0.001-0.005 depending on PDF length)

---

### Agent 2: Job Scraper

**File:** `agents/job_scraper.py`

**Purpose:** Find relevant job postings from multiple sources

#### Process Flow

```
User Query → Query Expansion (OpenAI) →
Multi-Source Search (JSearch + Brave) →
Deduplication → Balanced Results
```

#### Implementation Details

**1. Query Expansion**

Converts informal queries to formal job titles:
```
"ai student" → [
  "AI Intern",
  "Junior AI Engineer",
  "Machine Learning Intern",
  "AI Research Intern",
  "Data Science Intern"
]
```

- **Model:** `gpt-4o-mini`
- **Output:** 3-5 variations for broader coverage

**2. Multi-Source Search**

##### Source A: JSearch API (via RapidAPI)

**Strategy with fallback logic:**

1. **Strategy 1:** Search with location
   `"{job_title} in {location}"`

2. **Strategy 2:** Search with "Remote" (if Strategy 1 fails)
   `"{job_title} remote"`

3. **Strategy 3:** Global search (if Strategy 2 fails)
   `"{job_title}"`

**Endpoint:** `https://jsearch.p.rapidapi.com/search`

**Parameters:**
- `query`: job title + location
- `num_pages`: 1
- `page`: 1

##### Source B: Brave Search API

**Purpose:** Web-wide job discovery

Uses `BraveSearchAgent` for:
- Job board aggregation
- Company career pages
- Israeli job sites
- Filters out LinkedIn profiles and non-job content

**3. Deduplication**

Two-level deduplication:
1. **By URL:** Remove duplicate job postings with same link
2. **By (title, company):** Remove same job from different sources

**4. Result Balancing**

- Split 50/50 between JSearch and Brave Search
- If one source has fewer results, fill from the other
- Total results match `num_jobs` parameter

#### Output Structure

```python
[
    Job(
        title="Senior Python Developer",
        company="TechCorp Israel",
        location="Tel Aviv, Israel",
        description="We are looking for...",
        url="https://...",
        posted_date="2025-10-18",
        source="jsearch"
    ),
    ...
]
```

#### Technologies Used
- **OpenAI GPT-4o-mini:** Query expansion
- **JSearch API (RapidAPI):** Job board aggregation
- **Brave Search API:** Web-wide job discovery
- **Requests:** HTTP client

#### API Costs
- **1 OpenAI call** for query expansion (~$0.001)
- **N × M calls** to JSearch/Brave (varies by subscription)

---

## 3. Stage 2: Company Intelligence (Parallel)

### Agent 3: News Agent

**File:** `agents/news_agent.py`

**Purpose:** Gather company insights and sentiment from Reddit + AI analysis

#### Process Flow

```
Company Name → Reddit Search (PRAW) →
Sentiment Analysis → Brave Research →
OpenAI AI Insights → CompanyInsights Object
```

#### Implementation Details

**1. Reddit Intelligence Gathering**

**Subreddits searched:**
- `cscareerquestions`
- `experienceddevs`
- `programming`
- `jobs`

**Process:**
```python
for subreddit_name in subreddits:
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.search(company_name, limit=20):
        # Validate company name appears in post
        if company_name.lower() in submission.title.lower():
            posts.append(submission)
```

**Validation:** Company name must appear in post title/body to prevent false matches

**2. Sentiment Analysis**

**Keyword-based scoring:**

**Positive keywords:** "great", "love", "amazing", "best", "excellent"
**Negative keywords:** "bad", "terrible", "worst", "toxic", "hate"

**Calculation:**
```python
sentiment_score = (positive_count - negative_count) / total_posts
if sentiment_score > 0.2: "positive"
elif sentiment_score < -0.2: "negative"
else: "neutral"
```

**3. Data Extraction**

**Culture notes extraction:**
- Posts mentioning: "culture", "work-life", "remote", "benefits"
- Extract top 3-5 relevant highlights

**4. AI-Powered Analysis (Optional)**

If `role` parameter is provided:

**Step 1: Company Research**
- Use Brave Search API
- Query: `"{company_name} company interview process culture"`
- Extract top 3 results

**Step 2: AI Insights Generation**
- **Model:** `gpt-4o-mini`
- **Input:** Company name, role, Reddit highlights, research results
- **Output:** Structured interview prep brief

**Generated sections:**
- **About {company}:** What they do, main products/services
- **Interview Insights:** Process, culture patterns, technical stack
- **Red flags or positive signals**

**Format:** Markdown bullet points

**5. Fallback Strategy**

| Scenario | Action |
|----------|--------|
| Reddit timeout (>30s) | Return neutral sentiment, basic data |
| No relevant posts | Skip AI analysis, return empty insights |
| Brave Search fails | Continue with Reddit data only |
| OpenAI fails | Return Reddit insights without AI summary |

#### Output Structure

```python
CompanyInsights(
    company_name="TechCorp Israel",
    reddit_sentiment="positive",
    reddit_highlights=[
        "Great work-life balance according to 5 posts",
        "Remote-first culture mentioned frequently",
        "Competitive salaries in Tel Aviv market"
    ],
    recent_news=[
        "Active discussions about interview process",
        "Multiple developer testimonials"
    ],
    culture_notes=["Remote-first company", "Flexible hours"],
    ai_summary="""**About TechCorp Israel:**
    • Leading AI platform provider in EMEA
    • Focus on enterprise automation

    **Interview Insights:**
    • Technical interview includes system design
    • Culture emphasizes work-life balance

    **Signals:**
    • Positive: Strong employee satisfaction
    • Note: Rapid growth may mean high pace
    """,
    data_source="reddit_praw"
)
```

#### Technologies Used
- **PRAW (Python Reddit API Wrapper):** Reddit API client
- **OpenAI GPT-4o-mini:** AI insights generation
- **Brave Search API:** Company background research
- **Regex:** Text matching and validation
- **Asyncio:** Timeout protection (30s max)

#### API Costs
- **Reddit:** Free (within rate limits)
- **Brave Search:** 1 call per company (~$0.001-0.003)
- **OpenAI:** 1 call per company (~$0.005-0.01)

---

## 4. Stage 3: Matching & Ranking (Sequential)

### Agent 4: Smart Matcher

**File:** `agents/matcher.py`

**Purpose:** Calculate semantic similarity, rank jobs, generate recommendations

#### Process Flow

```
CV + Jobs → Create Embeddings →
Calculate Cosine Similarity →
Analyze Skill Overlap →
Apply Sentiment Bonus →
Calculate Final Score →
Sort & Rank
```

#### Implementation Details

**For each job:**

**1. Create CV Embedding**

```python
cv_text = f"""
Skills: {', '.join(cv_analysis.skills)}
Experience Level: {cv_analysis.experience_level}
Years of Experience: {cv_analysis.years_of_experience}
Desired Role: {desired_role}
Preferred Location: {desired_location}
"""
cv_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=cv_text
).data[0].embedding  # 1536-dimensional vector
```

**2. Create Job Embedding**

```python
job_text = f"{job.title}\n{job.description}"
job_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=job_text
).data[0].embedding  # 1536-dimensional vector
```

**3. Calculate Semantic Similarity**

**Cosine Similarity Formula:**
```python
dot_product = np.dot(cv_embedding, job_embedding)
magnitude_cv = np.linalg.norm(cv_embedding)
magnitude_job = np.linalg.norm(job_embedding)

similarity = dot_product / (magnitude_cv * magnitude_job)
# Result: 0 (completely different) to 1 (identical)
```

**Base Score Calculation:**
```python
base_score = similarity * 70  # 0-70 points
```

**4. Calculate Skill Overlap**

**Extract overlapping skills:**
```python
overlapping_skills = []
for skill in cv_analysis.skills:
    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
    if re.search(pattern, job.description.lower()):
        overlapping_skills.append(skill)
```

**Extract skill gaps:**
```python
common_skills = ["Python", "Docker", "Kubernetes", "AWS", ...]
skill_gaps = []
for skill in common_skills:
    if skill.lower() in job.description.lower():
        if skill not in cv_analysis.skills:
            skill_gaps.append(skill)
```

**Skill Bonus:**
```python
skill_match_ratio = len(overlapping_skills) / len(cv_analysis.skills)
skill_bonus = skill_match_ratio * 20  # 0-20 points
```

**Skill Penalty:**
```python
skill_penalty = min(len(skill_gaps) * 2, 10)  # Max 10 points
```

**5. Apply Company Insights Bonus**

```python
if insights.reddit_sentiment == "positive":
    sentiment_bonus = 5
elif insights.reddit_sentiment == "negative":
    sentiment_bonus = -10
else:
    sentiment_bonus = 0
```

**6. Calculate Final Score**

```python
final_score = base_score + skill_bonus - skill_penalty + sentiment_bonus
final_score = max(0, min(100, final_score))  # Clamp to 0-100
```

**7. Generate Recommendation**

```python
if final_score >= 80: "Strong Match"
elif final_score >= 65: "Good Fit"
elif final_score >= 50: "Consider"
else: "Skip"
```

**8. Generate Reasoning**

```python
reasoning = [
    f"{'Strong' if final_score >= 80 else 'Good' if final_score >= 65 else 'Moderate'} fit with {final_score:.0f}% compatibility",
    f"{'Strong' if len(overlapping_skills) / len(cv_analysis.skills) > 0.7 else 'Partial'} skill alignment: {', '.join(overlapping_skills[:5])}",
]

if skill_gaps:
    reasoning.append(f"Missing skills: {', '.join(skill_gaps[:3])}")

if insights.reddit_sentiment == "positive":
    reasoning.append("Company has positive reviews")
elif insights.reddit_sentiment == "negative":
    reasoning.append("Warning: Company has negative reviews")
```

**9. Create JobMatch Object**

```python
JobMatch(
    job=job,
    company_insights=insights,
    match_score=78.5,
    skill_overlap=["Python", "Docker", "FastAPI"],
    skill_gaps=["Kubernetes", "Terraform"],
    recommendation="Good Fit",
    reasoning=[
        "Good fit with 78% compatibility",
        "Strong skill alignment: Python, Docker, FastAPI",
        "Missing skills: Kubernetes, Terraform",
        "Company has positive reviews"
    ]
)
```

**10. Sort Results**

```python
matches.sort(key=lambda x: x.match_score, reverse=True)
```

#### Technologies Used
- **OpenAI text-embedding-3-small:** Semantic embeddings
- **NumPy:** Vector mathematics (dot product, norms)
- **Regex:** Skill matching with word boundaries

#### API Costs
- **1 CV embedding + N job embeddings** (~$0.01-0.02 total)

#### Scoring Breakdown

| Component | Points | Description |
|-----------|--------|-------------|
| Semantic similarity | 0-70 | Cosine similarity between CV and job |
| Skill overlap bonus | 0-20 | Percentage of CV skills in job |
| Skill gap penalty | 0-10 | Missing required skills |
| Sentiment bonus | -10 to +5 | Company Reddit sentiment |
| **Total** | **0-100** | **Final match score** |

---

## 5. Data Models

**File:** `models/models.py`

All models use **Pydantic v2** with strict validation.

### Model 1: CVAnalysis

```python
class CVAnalysis(BaseModel):
    skills: List[str] = Field(default_factory=list)
    experience_level: Literal["Junior", "Mid", "Senior", "Lead"] = "Mid"
    years_of_experience: int = Field(ge=0, le=50, default=0)
    preferred_locations: List[str] = Field(default_factory=list)
    key_achievements: List[str] = Field(default_factory=list)
```

**Purpose:** Structured CV data extracted by Agent 1

**Validation:**
- `years_of_experience`: Must be 0-50
- `experience_level`: Must be one of 4 predefined levels

---

### Model 2: Job

```python
class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str] = None
    source: Literal["linkedin", "indeed", "direct", "jsearch", "brave_search", "adzuna"] = "direct"
```

**Purpose:** Standardized job posting structure

**Sources tracked:**
- `jsearch`: JSearch API results
- `brave_search`: Brave Search results
- `linkedin`, `indeed`, `adzuna`: Future integrations
- `direct`: Company career pages

---

### Model 3: CompanyInsights

```python
class CompanyInsights(BaseModel):
    company_name: str
    reddit_sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    reddit_highlights: List[str] = Field(default_factory=list)
    recent_news: List[str] = Field(default_factory=list)
    culture_notes: List[str] = Field(default_factory=list)
    data_source: str = "multiple"
    ai_summary: Optional[str] = None  # AI-generated interview prep
```

**Purpose:** Company intelligence from Reddit + AI analysis

**Sentiment levels:**
- `positive`: More positive than negative mentions (>0.2 threshold)
- `negative`: More negative mentions (<-0.2 threshold)
- `neutral`: Balanced or no data

---

### Model 4: JobMatch

```python
class JobMatch(BaseModel):
    job: Job
    company_insights: CompanyInsights
    match_score: float = Field(ge=0, le=100)
    skill_overlap: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    recommendation: Literal["Strong Match", "Good Fit", "Consider", "Skip"] = "Consider"
    reasoning: List[str] = Field(default_factory=list)
```

**Purpose:** Final ranked result combining all pipeline outputs

**Validation:**
- `match_score`: Clamped to 0-100
- `recommendation`: One of 4 predefined levels

---

## 6. API Layer

**File:** `api/server.py`

### Technology Stack

- **Framework:** Flask 3.0
- **CORS:** flask-cors for frontend communication
- **File handling:** werkzeug for secure uploads

### Endpoints

#### 1. POST /api/run-pipeline

**Purpose:** Trigger complete job matching pipeline

**Request:** FormData
```
full_name: string (required)
email: string (required)
phone: string (optional)
years_of_experience: string (optional)
job_title: string (required)
location: string (optional)
job_level: string (optional) - "student", "junior", "senior"
num_jobs: integer (default: 5)
cv_file: file (optional, PDF)
```

**Process:**
1. Validate required fields
2. Save uploaded CV to `cvs/uploaded_{filename}`
3. Expand job_level to query suffix
4. Create `JobFinderPipeline` instance
5. Run pipeline: `await pipeline.run(cv_path, job_title, location, num_jobs)`
6. Return JSON response

**Response:**
```json
{
    "matches": [
        {
            "job": {
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "Tel Aviv",
                "description": "...",
                "url": "https://...",
                "posted_date": "2025-10-18",
                "source": "jsearch"
            },
            "company_insights": {
                "company_name": "TechCorp",
                "reddit_sentiment": "positive",
                "reddit_highlights": [...],
                "ai_summary": "..."
            },
            "match_score": 78.5,
            "skill_overlap": ["Python", "Docker"],
            "skill_gaps": ["Kubernetes"],
            "recommendation": "Good Fit",
            "reasoning": [...]
        }
    ],
    "config": {
        "role": "Python Developer",
        "location": "Tel Aviv",
        "cv_analyzed": true,
        "num_jobs": 12
    },
    "user_info": {
        "full_name": "John Doe",
        "email": "john@example.com"
    },
    "message": "Found 12 job matches"
}
```

---

#### 2. GET /api/job-matches

**Purpose:** Retrieve latest job matches

**Response:**
```json
{
    "matches": [...],
    "config": {...}
}
```

---

#### 3. GET /api/health

**Purpose:** Health check

**Response:**
```json
{
    "status": "healthy",
    "matches_count": 12
}
```

---

## 7. Agent Deep Dive

### Summary Table

| Agent | File | Key Methods | API Calls | Purpose |
|-------|------|-------------|-----------|---------|
| CV Analyzer | `cv_analyzer.py` | `analyze(cv_path)` | 1 (GPT-4o-mini) | Extract CV data |
| Job Scraper | `job_scraper.py` | `search(job_title, location, num_jobs)` | 1 (GPT) + N (JSearch/Brave) | Find jobs |
| News Agent | `news_agent.py` | `get_insights(company_name, role)` | N (Reddit) + N (Brave) + N (GPT) | Company insights |
| Smart Matcher | `matcher.py` | `match_and_rank(cv, jobs, insights)` | 1 + N (embeddings) | Rank jobs |
| Brave Search | `brave_search.py` | `search_jobs(...)` / `search_company_info(...)` | N (Brave API) | Web search utility |

### Agent 1: CV Analyzer

**Location:** `agents/cv_analyzer.py`

**Class:** `CVAnalyzer`

**Key Methods:**
- `_read_pdf(cv_path)`: PyPDF2 text extraction
- `_clean_text(text)`: Whitespace normalization
- `_create_analysis_prompt(cv_text)`: OpenAI prompt creation
- `analyze(cv_path)`: Main entry (async)

**Error Handling:**
- Validates file exists before reading
- 120s timeout on OpenAI call
- Returns structured error if parsing fails

---

### Agent 2: Job Scraper

**Location:** `agents/job_scraper.py`

**Class:** `JobScraper`

**Key Methods:**
- `_expand_job_query(query)`: OpenAI query expansion
- `_search_jsearch_api(job_title, location, num_jobs)`: JSearch with fallback
- `_search_brave_search(job_title, location, num_jobs)`: Brave integration
- `search(job_title, location, num_jobs)`: Main orchestrator (async)

**Deduplication Strategy:**
1. Track seen URLs in set
2. Track (title, company) tuples in set
3. Skip duplicates during aggregation

**Result Balancing:**
- Target: 50% JSearch, 50% Brave
- Fill from available source if one is empty

---

### Agent 3: News Agent

**Location:** `agents/news_agent.py`

**Class:** `NewsAgent`

**Key Methods:**
- `_search_reddit_praw(company_name)`: Reddit data collection
- `_research_company_background(company_name)`: Brave research
- `_generate_ai_insights(role, company_name, insights)`: OpenAI analysis
- `get_insights(company_name, role)`: Main entry (async)

**Timeout Protection:**
```python
try:
    insights = await asyncio.wait_for(
        self._search_reddit_praw(company_name),
        timeout=30.0
    )
except asyncio.TimeoutError:
    return CompanyInsights(
        company_name=company_name,
        data_source="timeout"
    )
```

**Sentiment Calculation:**
```python
positive_words = ["great", "love", "amazing", "best", "excellent"]
negative_words = ["bad", "terrible", "worst", "toxic", "hate"]

positive_count = sum(1 for word in positive_words if word in text.lower())
negative_count = sum(1 for word in negative_words if word in text.lower())

sentiment_score = (positive_count - negative_count) / total_posts
```

---

### Agent 4: Smart Matcher

**Location:** `agents/matcher.py`

**Class:** `SmartMatcher`

**Key Methods:**
- `_create_embedding(text)`: OpenAI embeddings
- `_cosine_similarity(vec1, vec2)`: Vector similarity
- `_calculate_skill_overlap(cv_skills, job_description)`: Skill matching
- `_calculate_base_score(...)`: Score calculation
- `_apply_insights_bonus(base_score, insights)`: Sentiment adjustment
- `match_and_rank(cv_analysis, jobs, insights, ...)`: Main orchestrator (async)

**Math Details:**
```python
# Cosine similarity
def _cosine_similarity(self, vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    magnitude1 = np.linalg.norm(vec1)
    magnitude2 = np.linalg.norm(vec2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)
```

---

### Supporting Agent: Brave Search

**Location:** `agents/brave_search.py`

**Class:** `BraveSearchAgent`

**Key Methods:**
- `search_jobs(job_title, location, num_results)`: Job search
- `search_company_info(company_name, num_results)`: Company research
- `_parse_search_results(results, job_title)`: Result filtering

**Filtering Logic:**
- Remove LinkedIn profiles
- Remove hiring guides and tutorials
- Extract company name from URL or title

**Company Extraction:**
```python
# From URL
if "careers" in url or "jobs" in url:
    domain = urlparse(url).netloc
    company = domain.split('.')[0]

# From title
company = title.split(' - ')[0].strip()
```

---

## 8. Technologies & Libraries

### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **Pydantic** | >= 2.7.0 | Data validation & serialization |
| **python-dotenv** | >= 1.0.0 | Environment variable loading |
| **PyPDF2** | >= 3.0.0 | PDF text extraction |
| **requests** | >= 2.31.0 | HTTP requests |
| **openai** | >= 1.40.0 | OpenAI API client |
| **numpy** | >= 1.26.0 | Vector mathematics |
| **praw** | >= 7.7.0 | Reddit API wrapper |
| **flask** | >= 3.0.0 | Web framework |
| **flask-cors** | >= 4.0.0 | CORS support |

### External APIs Required

#### 1. OpenAI API

**Models used:**
- **gpt-4o-mini:** CV analysis, query expansion, AI insights
- **text-embedding-3-small:** Semantic similarity (1536 dimensions)

**Endpoints:**
- `chat.completions.create()` - Text generation
- `embeddings.create()` - Vector embeddings

---

#### 2. JSearch API (via RapidAPI)

**Purpose:** Job board aggregation

**Endpoint:** `https://jsearch.p.rapidapi.com/search`

**Sources covered:**
- Indeed
- LinkedIn
- Glassdoor
- ZipRecruiter
- And more...

---

#### 3. Brave Search API

**Purpose:** Web-wide job discovery + company research

**Endpoints:**
- Web search: `https://api.search.brave.com/res/v1/web/search`

**Use cases:**
- Finding jobs on company career pages
- Israeli job sites (AllJobs, Drushim, etc.)
- Company background research

---

#### 4. Reddit API (PRAW)

**Purpose:** Company sentiment and culture insights

**Authentication:** OAuth2 (client ID + secret)

**Rate limits:** 60 requests per minute

**Subreddits used:**
- r/cscareerquestions
- r/experienceddevs
- r/programming
- r/jobs

---

### Frontend Stack

**Framework:** React 18

**Key Dependencies:**
- React Hooks (useState)
- Fetch API for HTTP requests
- FormData for file uploads

**Styling:**
- CSS3 (Flexbox, Grid)
- CSS animations
- Responsive design

---

## 9. Communication Between Agents

### Orchestrator Pattern

**File:** `pipeline/orchestrator.py`

**Class:** `JobFinderPipeline`

**Key Method:** `async def run(cv_path, job_title, location, num_jobs)`

**Implementation:**

```python
async def run(self, cv_path, job_title, location, num_jobs):
    # Stage 1: Parallel execution
    cv_task = self._run_cv_analyzer(cv_path)
    jobs_task = self._run_job_scraper(job_title, location, num_jobs)

    cv_analysis, jobs = await asyncio.gather(cv_task, jobs_task)

    # Stage 2: Parallel per company
    company_insights = await self._run_news_agent(jobs, desired_role=job_title)

    # Stage 3: Sequential matching
    matches = await self._run_matcher(
        cv_analysis,
        jobs,
        company_insights,
        desired_role=job_title,
        desired_location=location
    )

    return matches
```

**Benefits of this pattern:**
- **No direct agent-to-agent communication:** All data flows through orchestrator
- **Agents are stateless:** Each agent can be tested independently
- **Type safety:** Pydantic models enforce contracts
- **Async-first:** Maximizes parallelism

---

## 10. Execution Timeline Example

**Scenario:** User searches for "Python Developer" in "Tel Aviv" with 15 results

```
T+0s    User submits form
        └─ API receives POST /api/run-pipeline

T+1s    Stage 1 begins (parallel)
        ├─ Agent 1: CV Analyzer starts reading PDF
        └─ Agent 2: Job Scraper starts query expansion

T+5s    Job Scraper: Expands "Python Developer" to 5 formal titles

T+8s    CV Analyzer: Calls OpenAI GPT-4o-mini, returns CVAnalysis

T+10s   Job Scraper: Searches JSearch API with 5 queries

T+15s   Job Scraper: Searches Brave Search API in parallel

T+22s   Stage 1 Complete
        └─ cv_analysis + 15 jobs ready

T+22s   Stage 2 begins (parallel for 15 companies)
        └─ News Agent processes all 15 companies simultaneously

T+45s   Stage 2 Complete
        └─ 15 CompanyInsights objects ready

T+45s   Stage 3 begins (sequential)
        └─ Smart Matcher starts

T+46s   Matcher: Creates CV embedding

T+47-60s Matcher: Creates job embeddings, calculates scores

T+60s   Stage 3 Complete
        └─ 15 JobMatch objects sorted by score

T+60s   API returns JSON response to frontend
```

**Total Execution Time:** ~60 seconds

**Performance Optimization:**
- Without parallel execution: ~105s (75% slower)
- Parallel Stage 1: Saves ~10s
- Parallel Stage 2: Saves ~35s

---

## 11. Error Handling & Resilience

### Agent 1: CV Analyzer

**Errors handled:**
- **FileNotFoundError:** If CV path doesn't exist
- **OpenAI timeout:** 120s limit with asyncio.wait_for
- **PDF parsing errors:** Returns empty CVAnalysis

---

### Agent 2: Job Scraper

**Fallback strategy:**
1. Strategy 1: Search with location
2. Strategy 2: Search with "Remote" if Strategy 1 fails
3. Strategy 3: Global search if Strategy 2 fails

**API key validation:**
- Checks for JSearch/Brave API keys
- Returns empty list if missing (doesn't crash)

---

### Agent 3: News Agent

**Timeout protection:**
- 30s timeout on Reddit search
- Returns neutral sentiment if timeout occurs

**PRAW connection validation:**
- Tests authentication before search
- Returns fallback insights if auth fails

---

### Agent 4: Smart Matcher

**Missing insights handling:**
- Creates default CompanyInsights if not found

**Division by zero protection:**
- Checks vector magnitudes before cosine similarity

**Score clamping:**
- Ensures final score is 0-100

---

## 12. Environment Configuration

**File:** `.env.example`

### Required Variables

```bash
# OpenAI (Required for all agents)
OPENAI_API_KEY=sk-...

# JSearch API (Optional - job search fallback)
JSEARCH_API_KEY=...
RAPIDAPI_HOST=jsearch.p.rapidapi.com

# Brave Search API (Optional - web search)
BRAVE_SEARCH_API_KEY=...

# Reddit API (Required for company insights)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=job-finder/1.0 by YourUsername

# Apify (Optional - advanced scraping)
APIFY_TOKEN=...
```

### Setup Instructions

1. **Copy example file:**
   ```bash
   cp .env.example .env
   ```

2. **Get OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Add to `.env`

3. **Get Reddit credentials:**
   - Go to https://www.reddit.com/prefs/apps
   - Create new app (script type)
   - Copy client ID and secret

4. **Get Brave Search key (optional):**
   - Go to https://brave.com/search/api/
   - Sign up for free tier

5. **Get JSearch key (optional):**
   - Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
   - Subscribe to free tier

---

## 13. Frontend Integration

### Components

#### SearchForm Component

**File:** `frontend/src/components/SearchForm.jsx`

**Features:**
- Collects user info and search parameters
- Uploads CV file
- Shows 4-step loading progress
- Passes results to parent component

---

#### JobCard Component

**File:** `frontend/src/components/JobCard.jsx`

**Features:**
- Displays match score with circular progress
- Shows recommendation badge (color-coded)
- Lists skill overlap and gaps
- Expandable company insights section
- AI-generated interview prep brief
- "Apply Now" button with external link

---

## 14. Performance & Cost Analysis

### Execution Time Breakdown

| Stage | Operation | Time (Avg) | Optimization |
|-------|-----------|------------|--------------|
| Stage 1a | CV Analysis | 8-12s | Parallel with 1b |
| Stage 1b | Job Search | 15-25s | Parallel with 1a |
| Stage 2 | Company Insights (×N) | 1-3s each | All in parallel |
| Stage 3 | Matching & Ranking | 1-2s per job | Sequential |
| **Total** | **15 jobs** | **~60s** | **45% faster vs sequential** |

### Cost per Search (Estimated)

| Operation | API Calls | Cost per Call | Total |
|-----------|-----------|---------------|-------|
| CV Analysis | 1 | $0.001-0.005 | $0.001-0.005 |
| Query Expansion | 1 | $0.001 | $0.001 |
| Job Search | 10-20 | Varies | $0 |
| Company Insights | 15 | $0.0005-0.001 | $0.0075-0.015 |
| Embeddings | 16 | $0.0001 | $0.0016 |
| **TOTAL** | | | **$0.03-0.05 USD** |

---

## Summary

Job Finder is a sophisticated AI-powered job matching system that combines:

1. **Intelligent CV Analysis** using OpenAI GPT-4o-mini
2. **Multi-source Job Aggregation** via JSearch + Brave Search
3. **Real-time Company Intelligence** from Reddit + web research
4. **Semantic Matching** using OpenAI embeddings and cosine similarity
5. **Smart Ranking** with skill overlap detection and sentiment analysis

**Key Strengths:**
- Async/parallel execution for optimal performance
- Resilient error handling with fallback strategies
- Type-safe data models with Pydantic v2
- Modular agent architecture for easy testing and extension
- Comprehensive company insights with AI-generated interview prep

**Total execution time:** ~60 seconds for 15 jobs
**Cost per search:** ~$0.03-0.05 USD

---

**Generated:** 2025-10-31
**Version:** 1.0