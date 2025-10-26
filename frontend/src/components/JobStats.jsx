import './JobStats.css'

function JobStats({ matches }) {
  const avgScore = matches.length > 0
    ? (matches.reduce((sum, m) => sum + m.match_score, 0) / matches.length).toFixed(1)
    : 0

  const strongMatches = matches.filter(m => m.match_score >= 80).length
  const goodFits = matches.filter(m => m.match_score >= 65 && m.match_score < 80).length

  const topMatch = matches.length > 0 ? matches[0] : null

  return (
    <div className="job-stats">
      <div className="stat-card">
        <div className="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{matches.length}</div>
          <div className="stat-label">Total Matches</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon success">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{strongMatches}</div>
          <div className="stat-label">Strong Matches</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon warning">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{avgScore}%</div>
          <div className="stat-label">Avg Match Score</div>
        </div>
      </div>

      {topMatch && (
        <div className="stat-card highlight">
          <div className="stat-icon primary">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-value">{topMatch.match_score.toFixed(0)}%</div>
            <div className="stat-label">Top Match: {topMatch.job.company}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default JobStats
