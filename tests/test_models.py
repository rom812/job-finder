"""
Quick test to verify all models work correctly
"""

from models.models import CVAnalysis, Job, CompanyInsights, JobMatch


def test_cv_analysis():
    """Test CVAnalysis model"""
    print("Testing CVAnalysis...")

    cv = CVAnalysis(
        skills=["Python", "FastAPI", "Docker"],
        experience_level="Mid",
        years_of_experience=3,
        preferred_locations=["Tel Aviv", "Remote"],
        key_achievements=["Built microservices"]
    )

    print(f"  ✅ CVAnalysis created: {cv.experience_level}, {len(cv.skills)} skills")
    assert cv.years_of_experience == 3
    assert cv.experience_level == "Mid"


def test_job():
    """Test Job model"""
    print("Testing Job...")

    job = Job(
        title="Python Developer",
        company="TechCorp",
        location="Tel Aviv",
        description="Looking for a Python developer",
        url="https://example.com/job",
        posted_date="2025-10-20",
        source="linkedin"
    )

    print(f"  ✅ Job created: {job.title} at {job.company}")
    assert job.source == "linkedin"


def test_company_insights():
    """Test CompanyInsights model"""
    print("Testing CompanyInsights...")

    insights = CompanyInsights(
        company_name="TechCorp",
        reddit_sentiment="positive",
        reddit_highlights=["Great culture", "Good WLB"],
        recent_news=["Raised Series B", "Launched new product"],
        culture_notes=["Flexible hours"],
        data_source="reddit+news"
    )

    print(f"  ✅ CompanyInsights created: {insights.company_name}, sentiment={insights.reddit_sentiment}")
    assert insights.reddit_sentiment == "positive"
    assert len(insights.reddit_highlights) == 2


def test_job_match():
    """Test JobMatch model (uses other models!)"""
    print("Testing JobMatch...")

    # Create sub-models first
    job = Job(
        title="Python Developer",
        company="TechCorp",
        location="Tel Aviv",
        description="Looking for Python developer",
        url="https://example.com/job"
    )

    insights = CompanyInsights(
        company_name="TechCorp",
        reddit_sentiment="positive"
    )

    # Create JobMatch
    match = JobMatch(
        job=job,
        company_insights=insights,
        match_score=85.5,
        skill_overlap=["Python", "FastAPI"],
        skill_gaps=["Kubernetes"],
        recommendation="Strong Match",
        reasoning=["Strong skill match", "Positive company culture"]
    )

    print(f"  ✅ JobMatch created: {match.match_score}/100, {match.recommendation}")
    assert match.match_score == 85.5
    assert match.recommendation == "Strong Match"
    assert match.job.company == "TechCorp"


def test_validation():
    """Test that validation works"""
    print("Testing validation...")

    try:
        # This should FAIL - invalid experience_level
        cv = CVAnalysis(
            skills=["Python"],
            experience_level="Expert",  # ❌ Not in Literal!
            years_of_experience=3
        )
        print("  ❌ Validation failed - should have caught invalid experience_level")
    except Exception as e:
        print(f"  ✅ Validation caught error: {type(e).__name__}")

    try:
        # This should FAIL - score > 100
        match = JobMatch(
            job=Job(title="Test", company="Test", location="Test", description="Test", url="http://test.com"),
            company_insights=CompanyInsights(company_name="Test"),
            match_score=150  # ❌ Greater than 100!
        )
        print("  ❌ Validation failed - should have caught score > 100")
    except Exception as e:
        print(f"  ✅ Validation caught error: {type(e).__name__}")


def main():
    print("🧪 Testing all Pydantic models\n")
    print("=" * 60)

    test_cv_analysis()
    test_job()
    test_company_insights()
    test_job_match()
    test_validation()

    print("=" * 60)
    print("\n🎉 ALL MODEL TESTS PASSED!")
    print("\n✅ models.py is working correctly!")
    print("\n📚 Next: Implement Agent 1 (CV Analyzer)")


if __name__ == "__main__":
    main()
