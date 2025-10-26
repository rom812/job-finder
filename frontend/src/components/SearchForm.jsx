import { useState } from 'react'
import './SearchForm.css'

function SearchForm({ onSearch, initialConfig }) {
  const [formData, setFormData] = useState({
    jobTitle: initialConfig?.role || '',
    location: initialConfig?.location || '',
    numJobs: 20,
    cvFile: null
  })
  const [isSearching, setIsSearching] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSearching(true)

    try {
      // Create FormData for file upload
      const formDataToSend = new FormData()
      formDataToSend.append('job_title', formData.jobTitle)
      formDataToSend.append('location', formData.location)
      formDataToSend.append('num_jobs', formData.numJobs)

      if (formData.cvFile) {
        formDataToSend.append('cv_file', formData.cvFile)
      }

      const response = await fetch('http://localhost:5001/api/run-pipeline', {
        method: 'POST',
        body: formDataToSend
      })

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const data = await response.json()
      console.log('Search successful! Data:', data)
      console.log('Matches:', data.matches)
      console.log('Config:', data.config)
      onSearch(data.matches, data.config)
      setShowForm(false)
    } catch (error) {
      console.error('Search error:', error)
      alert('Search failed. Make sure the backend is running.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setFormData({ ...formData, cvFile: file })
    } else {
      alert('Please select a PDF file')
      e.target.value = ''
    }
  }

  if (!showForm) {
    return (
      <button className="new-search-btn" onClick={() => setShowForm(true)}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        New Search
      </button>
    )
  }

  return (
    <div className="search-form-overlay">
      <div className="search-form-container">
        <div className="form-header">
          <h2>New Job Search</h2>
          <button className="close-btn" onClick={() => setShowForm(false)}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="search-form">
          <div className="form-group">
            <label htmlFor="jobTitle">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              Job Title / Role
            </label>
            <input
              id="jobTitle"
              type="text"
              value={formData.jobTitle}
              onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
              placeholder="e.g., Python Developer, Data Scientist"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              Location
            </label>
            <input
              id="location"
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="e.g., Tel Aviv, Remote, United States"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="numJobs">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="8" y1="6" x2="21" y2="6"/>
                <line x1="8" y1="12" x2="21" y2="12"/>
                <line x1="8" y1="18" x2="21" y2="18"/>
                <line x1="3" y1="6" x2="3.01" y2="6"/>
                <line x1="3" y1="12" x2="3.01" y2="12"/>
                <line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
              Number of Jobs
            </label>
            <input
              id="numJobs"
              type="number"
              min="1"
              max="50"
              value={formData.numJobs}
              onChange={(e) => setFormData({ ...formData, numJobs: parseInt(e.target.value) })}
            />
          </div>

          <div className="form-group">
            <label htmlFor="cvFile">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              CV / Resume (PDF) - Optional
            </label>
            <div className="file-input-wrapper">
              <input
                id="cvFile"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
              />
              {formData.cvFile && (
                <span className="file-name">{formData.cvFile.name}</span>
              )}
              {!formData.cvFile && (
                <span className="file-placeholder">Will use existing CV if not provided</span>
              )}
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={() => setShowForm(false)}>
              Cancel
            </button>
            <button type="submit" className="submit-btn" disabled={isSearching}>
              {isSearching ? (
                <>
                  <div className="spinner"></div>
                  Searching...
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                  </svg>
                  Start Search
                </>
              )}
            </button>
          </div>
        </form>

        {isSearching && (
          <div className="search-progress">
            <div className="progress-steps">
              <div className="progress-step active">
                <div className="step-icon">1</div>
                <div className="step-label">Analyzing CV</div>
              </div>
              <div className="progress-step active">
                <div className="step-icon">2</div>
                <div className="step-label">Searching Jobs</div>
              </div>
              <div className="progress-step active">
                <div className="step-icon">3</div>
                <div className="step-label">Company Insights</div>
              </div>
              <div className="progress-step active">
                <div className="step-icon">4</div>
                <div className="step-label">Matching & Ranking</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchForm
