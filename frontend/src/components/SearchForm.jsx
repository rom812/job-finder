import { useState } from 'react'
import './SearchForm.css'

// List of countries (excluding Israel)
const COUNTRIES = [
  'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
  'France', 'Netherlands', 'Switzerland', 'Sweden', 'Norway', 'Denmark',
  'Finland', 'Ireland', 'Belgium', 'Austria', 'Spain', 'Italy', 'Portugal',
  'Poland', 'Czech Republic', 'Japan', 'Singapore', 'New Zealand', 'Remote'
].sort()

const JOB_LEVELS = [
  { value: 'student', label: 'Student / Intern' },
  { value: 'junior', label: 'Junior' },
  { value: 'senior', label: 'Senior' }
]

function SearchForm({ onSearch, initialConfig }) {
  const [formData, setFormData] = useState({
    // Personal Details
    fullName: '',
    email: '',
    phone: '',

    // Job Search
    jobTitle: initialConfig?.role || '',
    country: initialConfig?.location || '',
    jobLevel: '',
    numJobs: 5,
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

      // Personal details
      formDataToSend.append('full_name', formData.fullName)
      formDataToSend.append('email', formData.email)
      formDataToSend.append('phone', formData.phone)

      // Job search parameters
      formDataToSend.append('job_title', formData.jobTitle)
      formDataToSend.append('location', formData.country)
      formDataToSend.append('job_level', formData.jobLevel)
      formDataToSend.append('num_jobs', formData.numJobs)

      if (formData.cvFile) {
        formDataToSend.append('cv_file', formData.cvFile)
      }

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'
      const response = await fetch(`${apiUrl}/api/run-pipeline`, {
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
          {/* Personal Details Section */}
          <div className="form-section">
            <h3 className="section-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Personal Details
            </h3>

            <div className="form-group">
              <label htmlFor="fullName">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder="e.g., John Doe"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                  </svg>
                  Phone (optional)
                </label>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+972-50-123-4567"
                />
              </div>
            </div>
          </div>

          {/* Job Search Section */}
          <div className="form-section">
            <h3 className="section-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              Job Search Criteria
            </h3>

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

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="country">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                  Country
                </label>
                <select
                  id="country"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  required
                >
                  <option value="">Select a country...</option>
                  {COUNTRIES.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="jobLevel">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  Job Level
                </label>
                <select
                  id="jobLevel"
                  value={formData.jobLevel}
                  onChange={(e) => setFormData({ ...formData, jobLevel: e.target.value })}
                  required
                >
                  <option value="">Select level...</option>
                  {JOB_LEVELS.map(level => (
                    <option key={level.value} value={level.value}>{level.label}</option>
                  ))}
                </select>
              </div>
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
