# Job Finder Frontend

Modern, minimalist, and futuristic UI for displaying job matches.

## Features

- **Real-time Job Matching Display**: See your CV matched against jobs with detailed scoring
- **Interactive Job Cards**: Expandable cards with company insights, skills analysis, and more
- **Smart Filtering**: Filter by match quality (Strong Match, Good Fit, Consider)
- **Company Insights**: Reddit sentiment, culture notes, and recent news
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern UI**: Dark theme with gradient accents and smooth animations

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Lightning-fast build tool
- **CSS3**: Custom CSS with animations and gradients

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## API Connection

The frontend connects to the Flask backend at `http://localhost:5000/api/job-matches`.

Make sure the backend is running before starting the frontend.

## Components

### JobDashboard
Main dashboard component with filtering and sorting controls.

### JobCard
Individual job card with expandable details, skills analysis, and company insights.

### JobStats
Statistics overview showing total matches, strong matches, and average scores.

### LoadingScreen
Animated loading screen while data is being fetched.

## Customization

### Colors

Edit the CSS variables in the component files to change the color scheme:

- Primary gradient: `#667eea` to `#764ba2`
- Background: `#0a0a0a` to `#1a1a2e`
- Success: `#10b981`
- Warning: `#f59e0b`
- Error: `#ef4444`

### Layout

The dashboard uses CSS Grid for responsive layouts. Adjust breakpoints in the CSS files as needed.
