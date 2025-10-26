#!/usr/bin/env python3
"""
Simple Flask Backend for Job Finder
Runs without heavy dependencies - just Flask!
"""

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("Installing Flask...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    from flask import Flask, jsonify, request
    from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock job data
MOCK_MATCHES = [
    {
        'job': {
            'title': 'Senior Python Developer',
            'company': 'TechCorp Israel',
            'location': 'Tel Aviv, Israel',
            'description': 'Looking for experienced Python developer with 5+ years experience in backend development. Strong knowledge of Python, FastAPI, Docker required.',
            'url': 'https://www.linkedin.com/jobs/view/123456',
            'posted_date': '2025-10-20',
            'source': 'linkedin'
        },
        'company_insights': {
            'company_name': 'TechCorp Israel',
            'reddit_sentiment': 'positive',
            'reddit_highlights': [
                'Great work-life balance',
                'Excellent learning opportunities',
                'Strong engineering culture'
            ],
            'recent_news': ['Series B funding completed', 'Expanding to Europe'],
            'culture_notes': ['Remote-friendly', 'Agile methodology'],
            'data_source': 'reddit'
        },
        'match_score': 92.5,
        'skill_overlap': ['Python', 'FastAPI', 'Docker', 'PostgreSQL', 'AWS'],
        'skill_gaps': ['Kubernetes', 'GraphQL'],
        'recommendation': 'Strong Match',
        'reasoning': [
            'Your Python expertise aligns perfectly with requirements',
            'Company culture matches your preferences',
            'Strong growth opportunity in established company'
        ]
    },
    {
        'job': {
            'title': 'Python Backend Engineer',
            'company': 'StartupXYZ',
            'location': 'Remote (Israel)',
            'description': 'Join our fast-growing startup as a Python Backend Engineer. Build scalable microservices and APIs.',
            'url': 'https://www.indeed.com/jobs/view/789012',
            'posted_date': '2025-10-19',
            'source': 'indeed'
        },
        'company_insights': {
            'company_name': 'StartupXYZ',
            'reddit_sentiment': 'positive',
            'reddit_highlights': [
                'Fast-paced environment',
                'Equity compensation',
                'Small team, big impact'
            ],
            'recent_news': ['Seed funding raised - $3M'],
            'culture_notes': ['Startup mentality', 'Flexible hours'],
            'data_source': 'reddit'
        },
        'match_score': 85.0,
        'skill_overlap': ['Python', 'REST API', 'SQL', 'Git'],
        'skill_gaps': ['Redis', 'Celery', 'RabbitMQ'],
        'recommendation': 'Good Fit',
        'reasoning': [
            'Good technical match with your skills',
            'Startup experience could be valuable',
            'Remote work availability'
        ]
    },
    {
        'job': {
            'title': 'Full Stack Developer (Python + React)',
            'company': 'DataScience Ltd',
            'location': 'Herzliya, Israel',
            'description': 'Looking for a Full Stack Developer with Python backend and React frontend experience.',
            'url': 'https://datascience.com/careers/fullstack',
            'posted_date': '2025-10-17',
            'source': 'direct'
        },
        'company_insights': {
            'company_name': 'DataScience Ltd',
            'reddit_sentiment': 'neutral',
            'reddit_highlights': [
                'Interesting technical challenges',
                'Data science focus',
                'Good compensation'
            ],
            'recent_news': ['Partnered with major cloud provider'],
            'culture_notes': ['Hybrid work model', 'Focus on innovation'],
            'data_source': 'reddit'
        },
        'match_score': 78.5,
        'skill_overlap': ['Python', 'Flask', 'PostgreSQL', 'Docker'],
        'skill_gaps': ['React', 'TypeScript', 'Data visualization'],
        'recommendation': 'Good Fit',
        'reasoning': [
            'Strong backend match with your experience',
            'Opportunity to learn frontend development',
            'Growing data science field'
        ]
    },
    {
        'job': {
            'title': 'DevOps Engineer (Python Focus)',
            'company': 'CloudTech Solutions',
            'location': 'Tel Aviv, Israel',
            'description': 'DevOps Engineer with strong Python scripting skills. Experience with AWS, Docker, Kubernetes required.',
            'url': 'https://www.linkedin.com/jobs/view/345678',
            'posted_date': '2025-10-21',
            'source': 'linkedin'
        },
        'company_insights': {
            'company_name': 'CloudTech Solutions',
            'reddit_sentiment': 'positive',
            'reddit_highlights': [
                'Great benefits',
                'Modern tech stack',
                'Work with latest cloud technologies'
            ],
            'recent_news': ['Became AWS Advanced Partner'],
            'culture_notes': ['Cloud-first approach', 'Continuous learning'],
            'data_source': 'reddit'
        },
        'match_score': 72.0,
        'skill_overlap': ['Python', 'AWS', 'Docker', 'Linux'],
        'skill_gaps': ['Kubernetes', 'Terraform', 'Monitoring tools'],
        'recommendation': 'Consider',
        'reasoning': [
            'Python skills transferable to DevOps',
            'Good opportunity to expand into infrastructure',
            'Stable company with good reputation'
        ]
    }
]

@app.route('/api/job-matches', methods=['GET'])
def get_job_matches():
    """Get job matches"""
    return jsonify({
        'matches': MOCK_MATCHES,
        'config': {
            'role': 'Python Developer',
            'location': 'Tel Aviv',
            'cv_analyzed': True,
            'num_jobs': len(MOCK_MATCHES)
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'matches_count': len(MOCK_MATCHES)
    })

@app.route('/')
def index():
    """Root endpoint - API documentation"""
    return '''
    <html>
    <head><title>Job Finder API</title></head>
    <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
        <h1>🚀 Job Finder Backend API</h1>
        <p>Backend is running successfully!</p>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/api/health">GET /api/health</a> - Health check</li>
            <li><a href="/api/job-matches">GET /api/job-matches</a> - Get job matches</li>
            <li>POST /api/run-pipeline - Run job search pipeline</li>
        </ul>
        <h2>Frontend:</h2>
        <p>👉 <a href="http://localhost:5173" target="_blank">Open Frontend (http://localhost:5173)</a></p>
    </body>
    </html>
    '''

@app.route('/api/run-pipeline', methods=['POST', 'OPTIONS'])
def run_pipeline():
    """Mock run pipeline endpoint"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    # Get form data from request
    job_title = request.form.get('job_title', 'Python Developer')
    location = request.form.get('location', 'Tel Aviv')
    num_jobs = int(request.form.get('num_jobs', 4))

    # Limit matches to requested number
    matches = MOCK_MATCHES[:num_jobs]

    print(f"\n🔍 New search request:")
    print(f"   Job Title: {job_title}")
    print(f"   Location: {location}")
    print(f"   Num Jobs: {num_jobs}")
    print(f"   Returning {len(matches)} matches\n")

    return jsonify({
        'matches': matches,
        'config': {
            'role': job_title,
            'location': location,
            'cv_analyzed': True,
            'num_jobs': len(matches)
        },
        'message': f'Found {len(matches)} job matches for {job_title} in {location}'
    })

if __name__ == '__main__':
    print('')
    print('=' * 80)
    print('🚀 Job Finder Backend API Server')
    print('=' * 80)
    print('')
    print('📍 Running on: http://localhost:5001')
    print('')
    print('Endpoints:')
    print('  GET  http://localhost:5001/api/job-matches')
    print('  GET  http://localhost:5001/api/health')
    print('  POST http://localhost:5001/api/run-pipeline')
    print('')
    print('=' * 80)
    print('')
    print('✅ Server ready! Press Ctrl+C to stop')
    print('')

    app.run(host='0.0.0.0', port=5001, debug=False)
