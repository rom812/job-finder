# Frontend Guide

Complete guide for using the Job Finder web interface.

## Overview

The Job Finder frontend is a modern, minimalist web application that displays your job matches in a beautiful and intuitive way. Built with React and designed with a futuristic dark theme.

## Getting Started

### 1. Install Dependencies

First time setup:

```bash
cd frontend
npm install
cd ..
```

### 2. Start the Backend API

The frontend needs the backend API to fetch job matches data:

```bash
source venv/bin/activate
python api/server.py
```

The API will:
- Load sample job matches data
- Start server on `http://localhost:5000`
- Provide endpoints for the frontend

### 3. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Quick Start Script

Or use the all-in-one script:

```bash
./run_with_frontend.sh
```

This starts both backend and frontend automatically.

## Features

### Job Dashboard

The main dashboard shows all your job matches with:

- **Total matches count**
- **Strong matches** (80%+ score)
- **Average match score**
- **Top match highlight**

### Filtering

Filter jobs by match quality:

- **All**: Show all jobs
- **Strong Match**: 80%+ score
- **Good Fit**: 65-79% score
- **Consider**: 50-64% score

### Sorting

Sort jobs by:

- **Match Score**: Highest scoring jobs first (default)
- **Posted Date**: Most recent jobs first

### Job Cards

Each job card displays:

**Header (Always Visible)**:
- Rank number
- Job title
- Company name
- Location
- Match score (circular progress)
- Recommendation badge
- Source (LinkedIn, Indeed, Direct)
- Posted date
- Company sentiment

**Expandable Details** (Click to expand):
- **Why This Match**: AI reasoning for the match
- **Your Matching Skills**: Skills you have that match the job
- **Skills to Learn**: Skills the job requires that you don't have yet
- **Company Insights**:
  - Reddit highlights
  - Culture notes
  - Recent news
- **Actions**:
  - Apply Now button (opens job posting)
  - Save button (bookmark for later)

## Understanding Match Scores

### Score Colors

- **Green** (80-100): Strong Match - Highly recommended
- **Orange** (65-79): Good Fit - Worth considering
- **Purple** (50-64): Consider - May need skill development
- **Red** (<50): Skip - Not a good match

### Score Components

Match scores are calculated based on:

1. **Skills Match** (40%): How many required skills you have
2. **Experience Level** (20%): Match between your level and job requirements
3. **Location Preference** (15%): Geographic fit
4. **Company Culture** (15%): Culture alignment
5. **Career Growth** (10%): Growth opportunities

## Company Insights

### Reddit Sentiment

Shows what people are saying about the company on Reddit:

- **Positive**: Generally good feedback
- **Neutral**: Mixed or limited feedback
- **Negative**: Concerning feedback

### Culture Notes

Tags describing the company culture:
- Remote-friendly
- Startup mentality
- Work-life balance
- Agile methodology
- Learning culture

### Recent News

Latest news about the company:
- Funding rounds
- Product launches
- Expansion plans
- Awards and recognition

## Responsive Design

The frontend works perfectly on:

- **Desktop**: Full layout with all features
- **Tablet**: Optimized grid layout
- **Mobile**: Single column, touch-friendly

## Customization

### Changing Colors

Edit the CSS files in `frontend/src/components/`:

**Primary Colors**:
```css
/* Gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success (Green) */
color: #10b981;

/* Warning (Orange) */
color: #f59e0b;

/* Error (Red) */
color: #ef4444;
```

**Background**:
```css
/* Dark background gradient */
background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
```

### Changing Layout

The layout uses CSS Grid. Edit breakpoints in component CSS files:

```css
@media (max-width: 768px) {
  /* Tablet styles */
}

@media (max-width: 640px) {
  /* Mobile styles */
}
```

## API Integration

### Endpoints Used

**GET /api/job-matches**
- Returns all job matches and search configuration
- Called on initial load and refresh

**GET /api/health**
- Health check endpoint
- Shows backend status

### Data Flow

1. Frontend requests data from API
2. If API is unavailable, uses mock data
3. Displays matches in the dashboard
4. Updates automatically on refresh

### Mock Data

When the backend is unavailable, the frontend uses built-in mock data with 3 sample job matches. This is useful for:

- Frontend development
- Design testing
- Demos

## Troubleshooting

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend connection error

Make sure the backend is running:
```bash
curl http://localhost:5000/api/health
```

If not running:
```bash
source venv/bin/activate
python api/server.py
```

### Port already in use

Change the port in `vite.config.js`:

```js
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000  // Change from default 5173
  }
})
```

### CORS errors

Make sure Flask-CORS is installed:
```bash
pip install flask-cors
```

## Development

### Hot Reload

Vite provides instant hot reload. Changes to:
- React components
- CSS files
- JavaScript files

Will update immediately in the browser.

### Building for Production

```bash
cd frontend
npm run build
```

This creates optimized files in `frontend/dist/`

### Preview Production Build

```bash
npm run preview
```

## Performance

### Load Time

- Initial load: ~1-2 seconds
- Subsequent navigation: Instant
- API calls: ~500ms

### Optimization

The frontend is optimized with:
- Code splitting
- CSS minification
- Asset compression
- Lazy loading for images

## Browser Support

Tested and working on:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Planned features:

1. **Search Functionality**: Search within job matches
2. **Save/Bookmark**: Persist saved jobs
3. **Export**: Export matches to PDF/CSV
4. **Notifications**: Alert for new high-scoring matches
5. **Comparison**: Compare multiple jobs side-by-side
6. **Analytics**: Track application success rate

## Questions?

- Check [README.md](README.md) for general project info
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [PARTNERSHIP_GUIDE.md](PARTNERSHIP_GUIDE.md) for collaboration

---

Happy job hunting!
