"""
Data models for job-finder project using Pydantic v2
All models include validation and type hints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ============================================================================
# Model 1: CVAnalysis
# ============================================================================
# This model represents the output of the CV Analyzer agent
# It contains structured information extracted from a resume/CV

class CVAnalysis(BaseModel):
    """
    Structured data extracted from a CV/Resume

    This is the output of Agent 1 (CV Analyzer)
    """
    # List of technical skills (e.g., ["Python", "Docker", "AWS"])
    skills: List[str] = Field(
        default_factory=list,
        description="List of technical skills found in CV"
    )

    # Experience level - must be one of these exact values
    experience_level: Literal["Junior", "Mid", "Senior", "Lead"] = Field(
        default="Mid",
        description="Career level based on CV analysis"
    )

    # Years of professional experience
    years_of_experience: int = Field(
        ge=0,  # Greater or Equal to 0
        le=50,  # Less or Equal to 50
        default=0,
        description="Total years of professional experience"
    )

    # Preferred work locations
    preferred_locations: List[str] = Field(
        default_factory=list,
        description="Locations mentioned in CV (e.g., ['Tel Aviv', 'Remote'])"
    )

    # Key achievements from CV
    key_achievements: List[str] = Field(
        default_factory=list,
        description="Notable achievements or projects mentioned"
    )

    # Example usage in docstring:
    """
    Example:
        cv = CVAnalysis(
            skills=["Python", "FastAPI", "PostgreSQL"],
            experience_level="Mid",
            years_of_experience=3,
            preferred_locations=["Tel Aviv", "Remote"],
            key_achievements=["Built microservices architecture"]
        )
    """


# ============================================================================
# TODO: Model 2 - Job
# ============================================================================# YOUR TURN! Write the Job model here# Hint: Look at ARCHITECTURE.md lines 277-285
# Fields needed: title, company, location, description, url, posted_date, source
class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str] = None
    source: Literal["linkedin", "indeed", "direct", "jsearch"] = "direct"



# ============================================================================
# TODO: Model 3 - CompanyInsights
# ============================================================================# YOUR TURN! Write the CompanyInsights model here
# Fields needed: company_name, reddit_sentiment, reddit_highlights, recent_news, culture_notes, data_source
class CompanyInsights(BaseModel):
    company_name: str
    reddit_sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    reddit_highlights: List[str] = Field(default_factory=list)
    recent_news: List[str] = Field(default_factory=list)
    culture_notes: List[str] = Field(default_factory=list)
    data_source: str = "multiple"
# ============================================================================
# TODO: Model 4 - JobMatch
# ============================================================================
# Fields needed: job, company_insights, match_score, skill_overlap, skill_gaps, recommendation, reasoning
class JobMatch(BaseModel):
    job: Job
    company_insights: CompanyInsights
    match_score: float = Field(ge=0, le=100)
    skill_overlap: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    recommendation: Literal["Strong Match", "Good Fit", "Consider", "Skip"] = "Consider"
    reasoning: List[str] = Field(default_factory=list)


