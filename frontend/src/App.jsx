import { useState, useEffect } from 'react'
import './App.css'
import JobDashboard from './components/JobDashboard'
import LoadingScreen from './components/LoadingScreen'
import SearchForm from './components/SearchForm'

function App() {
  const [jobMatches, setJobMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchConfig, setSearchConfig] = useState(null)

  useEffect(() => {
    fetchJobMatches()
  }, [])

  const handleNewSearch = (matches, config) => {
    console.log('🔍 handleNewSearch called!')
    console.log('📊 New matches:', matches)
    console.log('⚙️ New config:', config)
    setJobMatches(matches)
    setSearchConfig(config)
    setLoading(false)
    console.log('✅ State updated!')
  }

  const fetchJobMatches = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:5001/api/job-matches')

      if (!response.ok) {
        throw new Error('Failed to fetch job matches')
      }

      const data = await response.json()
      setJobMatches(data.matches || [])
      setSearchConfig(data.config || null)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching job matches:', err)
      setError(err.message)
      setLoading(false)
      // Use mock data for development
      loadMockData()
    }
  }

  const loadMockData = () => {
    // Mock data matching the orchestrator output structure
    const mockMatches = [
      {
        job: {
          title: "Senior Python Developer",
          company: "TechCorp Israel",
          location: "Tel Aviv, Israel",
          description: "We're looking for a Senior Python Developer...",
          url: "https://example.com/jobs/1",
          posted_date: "2025-10-18",
          source: "linkedin"
        },
        company_insights: {
          company_name: "TechCorp Israel",
          reddit_sentiment: "positive",
          reddit_highlights: [
            "Great work-life balance",
            "Excellent learning opportunities",
            "Strong engineering culture"
          ],
          recent_news: ["Series B funding completed", "Expanding to Europe"],
          culture_notes: ["Remote-friendly", "Agile methodology"],
          data_source: "reddit"
        },
        match_score: 92.5,
        skill_overlap: ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS"],
        skill_gaps: ["Kubernetes", "GraphQL"],
        recommendation: "Strong Match",
        reasoning: [
          "Your Python expertise aligns perfectly with requirements",
          "Company culture matches your preferences",
          "Strong growth opportunity in established company"
        ]
      },
      {
        job: {
          title: "Python Backend Engineer",
          company: "StartupXYZ",
          location: "Remote (Israel)",
          description: "Join our fast-growing startup...",
          url: "https://example.com/jobs/2",
          posted_date: "2025-10-19",
          source: "indeed"
        },
        company_insights: {
          company_name: "StartupXYZ",
          reddit_sentiment: "positive",
          reddit_highlights: [
            "Fast-paced environment",
            "Equity compensation"
          ],
          recent_news: ["Seed funding raised"],
          culture_notes: ["Startup mentality", "Flexible hours"],
          data_source: "reddit"
        },
        match_score: 85.0,
        skill_overlap: ["Python", "REST API", "SQL", "Git"],
        skill_gaps: ["Redis", "Celery"],
        recommendation: "Good Fit",
        reasoning: [
          "Good technical match",
          "Startup experience could be valuable",
          "Remote work availability"
        ]
      },
      {
        job: {
          title: "Full Stack Developer (Python + Vue.js)",
          company: "DataScience Ltd",
          location: "Herzliya, Israel",
          description: "Looking for a Full Stack Developer...",
          url: "https://example.com/jobs/3",
          posted_date: "2025-10-17",
          source: "direct"
        },
        company_insights: {
          company_name: "DataScience Ltd",
          reddit_sentiment: "neutral",
          reddit_highlights: [
            "Interesting technical challenges",
            "Data science focus"
          ],
          recent_news: [],
          culture_notes: ["Hybrid work model"],
          data_source: "reddit"
        },
        match_score: 78.5,
        skill_overlap: ["Python", "Flask", "PostgreSQL", "Docker"],
        skill_gaps: ["Vue.js", "Data visualization"],
        recommendation: "Good Fit",
        reasoning: [
          "Strong backend match",
          "Opportunity to learn frontend",
          "Growing data science field"
        ]
      }
    ]

    setJobMatches(mockMatches)
    setSearchConfig({
      role: "Python Developer",
      location: "Tel Aviv",
      cv_analyzed: true
    })
    setLoading(false)
  }

  if (loading) {
    return <LoadingScreen />
  }

  if (error && jobMatches.length === 0) {
    return (
      <div className="error-container">
        <h2>Error Loading Jobs</h2>
        <p>{error}</p>
        <button onClick={fetchJobMatches}>Retry</button>
      </div>
    )
  }

  return (
    <div className="app">
      <SearchForm onSearch={handleNewSearch} initialConfig={searchConfig} />
      <JobDashboard
        jobMatches={jobMatches}
        searchConfig={searchConfig}
        onRefresh={fetchJobMatches}
      />
    </div>
  )
}

export default App
