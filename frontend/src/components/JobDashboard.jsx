import { useState } from 'react'
import './JobDashboard.css'
import JobCard from './JobCard'
import JobStats from './JobStats'

function JobDashboard({ jobMatches, searchConfig, onRefresh }) {
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score')

  const filterMatches = (matches) => {
    let filtered = [...matches]

    // Apply filter
    if (filter !== 'all') {
      filtered = filtered.filter(match => {
        if (filter === 'strong') return match.match_score >= 80
        if (filter === 'good') return match.match_score >= 65 && match.match_score < 80
        if (filter === 'consider') return match.match_score >= 50 && match.match_score < 65
        return true
      })
    }

    // Apply sorting
    if (sortBy === 'score') {
      filtered.sort((a, b) => b.match_score - a.match_score)
    } else if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.job.posted_date) - new Date(a.job.posted_date))
    }

    return filtered
  }

  const filteredMatches = filterMatches(jobMatches)

  return (
    <div className="job-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1>Job Matches</h1>
            {searchConfig && (
              <div className="search-info">
                <span className="info-badge">{searchConfig.role}</span>
                <span className="info-badge">{searchConfig.location}</span>
                <span className="info-badge success">CV Analyzed</span>
              </div>
            )}
          </div>
          <button className="refresh-btn" onClick={onRefresh}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
            </svg>
            Refresh
          </button>
        </div>
      </header>

      <JobStats matches={jobMatches} />

      <div className="controls">
        <div className="filters">
          <button
            className={filter === 'all' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('all')}
          >
            All ({jobMatches.length})
          </button>
          <button
            className={filter === 'strong' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('strong')}
          >
            Strong Match ({jobMatches.filter(m => m.match_score >= 80).length})
          </button>
          <button
            className={filter === 'good' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('good')}
          >
            Good Fit ({jobMatches.filter(m => m.match_score >= 65 && m.match_score < 80).length})
          </button>
          <button
            className={filter === 'consider' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('consider')}
          >
            Consider ({jobMatches.filter(m => m.match_score >= 50 && m.match_score < 65).length})
          </button>
        </div>

        <div className="sort-controls">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Match Score</option>
            <option value="date">Posted Date</option>
          </select>
        </div>
      </div>

      <div className="jobs-grid">
        {filteredMatches.length > 0 ? (
          filteredMatches.map((match, index) => (
            <JobCard key={index} match={match} rank={index + 1} />
          ))
        ) : (
          <div className="no-results">
            <p>No jobs match your current filters</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default JobDashboard
