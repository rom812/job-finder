import { useState } from 'react'
import './JobCard.css'

function JobCard({ match, rank }) {
  const [expanded, setExpanded] = useState(false)

  const getScoreColor = (score) => {
    if (score >= 80) return 'score-high'
    if (score >= 65) return 'score-medium'
    if (score >= 50) return 'score-low'
    return 'score-very-low'
  }

  const getSentimentIcon = (sentiment) => {
    if (sentiment === 'positive') return '😊'
    if (sentiment === 'negative') return '😟'
    return '😐'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Recently'
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return `${Math.floor(diffDays / 30)} months ago`
  }

  return (
    <div className={`job-card ${expanded ? 'expanded' : ''}`}>
      <div className="card-header" onClick={() => setExpanded(!expanded)}>
        <div className="rank-badge">#{rank}</div>
        <div className="job-title-section">
          <h3>{match.job.title}</h3>
          <div className="company-info">
            <span className="company-name">{match.job.company}</span>
            <span className="location">{match.job.location}</span>
          </div>
        </div>
        <div className={`match-score ${getScoreColor(match.match_score)}`}>
          <div className="score-circle">
            <svg viewBox="0 0 36 36" className="circular-chart">
              <path
                className="circle-bg"
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="circle"
                strokeDasharray={`${match.match_score}, 100`}
                d="M18 2.0845
                  a 15.9155 15.9155 0 0 1 0 31.831
                  a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="score-text">{Math.round(match.match_score)}</span>
          </div>
        </div>
        <div className="expand-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>

      <div className="card-tags">
        <span className={`tag recommendation-tag ${match.recommendation.toLowerCase().replace(' ', '-')}`}>
          {match.recommendation}
        </span>
        <span className="tag source-tag">{match.job.source}</span>
        <span className="tag date-tag">{formatDate(match.job.posted_date)}</span>
        <span className="tag sentiment-tag">
          {getSentimentIcon(match.company_insights.reddit_sentiment)} {match.company_insights.reddit_sentiment}
        </span>
      </div>

      {expanded && (
        <div className="card-details">
          <div className="details-section">
            <h4>Why This Match?</h4>
            <ul className="reasoning-list">
              {match.reasoning.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          </div>

          <div className="skills-section">
            <div className="skills-column">
              <h4>Your Matching Skills</h4>
              <div className="skills-tags">
                {match.skill_overlap.map((skill, idx) => (
                  <span key={idx} className="skill-tag match">{skill}</span>
                ))}
              </div>
            </div>
            {match.skill_gaps.length > 0 && (
              <div className="skills-column">
                <h4>Skills to Learn</h4>
                <div className="skills-tags">
                  {match.skill_gaps.map((skill, idx) => (
                    <span key={idx} className="skill-tag gap">{skill}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="details-section">
            <h4>Company Insights</h4>
            {match.company_insights.ai_summary ? (
              <div className="insights-group">
                <h5>Interview Prep Insights</h5>
                <div className="ai-insights">
                  {match.company_insights.ai_summary.split('\n').map((line, idx) => {
                    // Skip empty lines
                    if (!line.trim()) return null;
                    // Check if it's a bullet point
                    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
                      return <div key={idx} className="insight-bullet">{line.trim()}</div>;
                    }
                    // Otherwise render as paragraph
                    return <p key={idx} className="insight-text">{line}</p>;
                  })}
                </div>
              </div>
            ) : match.company_insights.reddit_highlights.length > 0 && (
              <div className="insights-group">
                <h5>Reddit Highlights</h5>
                <ul className="highlights-list">
                  {match.company_insights.reddit_highlights.map((highlight, idx) => (
                    <li key={idx}>{highlight}</li>
                  ))}
                </ul>
              </div>
            )}
            {match.company_insights.culture_notes.length > 0 && (
              <div className="insights-group">
                <h5>Culture Notes</h5>
                <div className="culture-tags">
                  {match.company_insights.culture_notes.map((note, idx) => (
                    <span key={idx} className="culture-tag">{note}</span>
                  ))}
                </div>
              </div>
            )}
            {match.company_insights.recent_news.length > 0 && (
              <div className="insights-group">
                <h5>Recent News</h5>
                <ul className="news-list">
                  {match.company_insights.recent_news.map((news, idx) => (
                    <li key={idx}>{news}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="card-actions">
            <a
              href={match.job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="apply-btn"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              Apply Now
            </a>
            <button className="save-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
              </svg>
              Save
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default JobCard
