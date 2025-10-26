import './LoadingScreen.css'

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loader">
          <div className="loader-inner"></div>
        </div>
        <h2>Analyzing Job Matches</h2>
        <p>Processing your career opportunities...</p>
      </div>
    </div>
  )
}

export default LoadingScreen
