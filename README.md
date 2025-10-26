# Job Finder

AI-powered job matching system with a modern web interface.

## Overview

Job Finder is an intelligent job search assistant that analyzes your CV, searches for relevant jobs, gathers company insights, and provides smart matching with detailed recommendations.

## Features

- **CV Analysis**: Automatically extracts skills, experience level, and preferences
- **Job Search**: Searches multiple job boards (LinkedIn, Indeed, etc.)
- **Company Insights**: Gathers Reddit discussions, news, and culture information
- **Smart Matching**: AI-powered matching algorithm with detailed scoring
- **Modern Web UI**: Beautiful, responsive frontend for viewing matches

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- Reddit API credentials (optional, mock data available)

### Installation

1. Clone the repository
2. Set up Python backend:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
cd ..
```

4. Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=job-finder/1.0
```

### Running the Application

#### Option 1: Full Stack (Recommended)
```bash
./run_with_frontend.sh
```

This starts:
- Flask API server at `http://localhost:5000`
- React frontend at `http://localhost:5173`

#### Option 2: Backend Only
```bash
source venv/bin/activate
python api/server.py
```

#### Option 3: Command Line
```bash
source venv/bin/activate
python pipeline/orchestrator.py
```

## Project Structure

```
job-finder/
├── agents/              # AI agents for different tasks
│   ├── cv_analyzer.py   # CV analysis agent
│   ├── job_scraper.py   # Job search agent
│   ├── news_agent.py    # Company insights agent
│   └── matcher.py       # Smart matching agent
├── api/                 # Flask API server
│   └── server.py
├── frontend/            # React web interface
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
├── models/              # Pydantic data models
├── pipeline/            # Pipeline orchestrator
├── tests/               # Unit tests
└── cvs/                 # CV storage directory
```

## Architecture

The system uses a 4-agent architecture:

1. **CV Analyzer**: Extracts structured data from resumes
2. **Job Scraper**: Searches job boards for relevant positions
3. **News Agent**: Gathers company insights from Reddit and news sources
4. **Smart Matcher**: Matches CV to jobs using AI-powered scoring

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Frontend Features

- **Interactive Job Cards**: Expandable cards with detailed information
- **Smart Filtering**: Filter by match quality
- **Real-time Updates**: Live data from the backend
- **Responsive Design**: Works on all devices
- **Dark Theme**: Modern, eye-friendly design

## API Endpoints

- `GET /api/job-matches` - Get current job matches
- `GET /api/health` - Health check
- `POST /api/run-pipeline` - Trigger new search (coming soon)

## Development

### Backend
```bash
source venv/bin/activate
python -m pytest tests/
```

### Frontend
```bash
cd frontend
npm run dev
```

## Contributing

See [PARTNERSHIP_GUIDE.md](PARTNERSHIP_GUIDE.md) for partnership opportunities.

## License

MIT License