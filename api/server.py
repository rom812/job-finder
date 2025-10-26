"""
Flask API Server for Job Finder Frontend
Serves job matches data from the orchestrator
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.orchestrator import JobFinderPipeline

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global variable to store the latest job matches
latest_matches = []
search_config = {}


@app.route('/api/job-matches', methods=['GET'])
def get_job_matches():
    """
    Get the latest job matches
    Returns JSON with matches and config
    """
    return jsonify({
        'matches': [match_to_dict(m) for m in latest_matches],
        'config': search_config
    })


@app.route('/api/run-pipeline', methods=['POST', 'OPTIONS'])
def run_pipeline():
    """
    Run the job finder pipeline with new parameters
    Accepts multipart/form-data with optional CV file upload
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    global latest_matches, search_config

    try:
        # Get form data
        job_title = request.form.get('job_title', '')
        location = request.form.get('location', '')
        num_jobs = int(request.form.get('num_jobs', 20))

        # Handle CV file upload (optional)
        cv_path = "cvs/romCV.pdf"  # Default CV
        if 'cv_file' in request.files:
            cv_file = request.files['cv_file']
            if cv_file.filename:
                # Save uploaded file
                filename = secure_filename(cv_file.filename)
                cv_path = f"cvs/uploaded_{filename}"
                cv_file.save(cv_path)

        # Validation
        if not job_title:
            return jsonify({'error': 'job_title is required'}), 400

        # Run pipeline asynchronously
        import asyncio
        pipeline = JobFinderPipeline(use_mock_data=False)

        # Run the pipeline
        matches = asyncio.run(pipeline.run(
            cv_path=cv_path,
            job_title=job_title,
            location=location,
            num_jobs=num_jobs
        ))

        # Update global state
        latest_matches = matches
        search_config = {
            'role': job_title,
            'location': location,
            'cv_analyzed': True,
            'num_jobs': len(matches)
        }

        return jsonify({
            'matches': [match_to_dict(m) for m in matches],
            'config': search_config,
            'message': f'Found {len(matches)} job matches'
        })

    except Exception as e:
        import traceback
        print(f"Error running pipeline: {e}")
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'message': 'Failed to run job search'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'matches_count': len(latest_matches)
    })


def match_to_dict(match):
    """
    Convert a JobMatch Pydantic model to a dictionary for JSON serialization
    """
    return {
        'job': {
            'title': match.job.title,
            'company': match.job.company,
            'location': match.job.location,
            'description': match.job.description,
            'url': match.job.url,
            'posted_date': match.job.posted_date,
            'source': match.job.source
        },
        'company_insights': {
            'company_name': match.company_insights.company_name,
            'reddit_sentiment': match.company_insights.reddit_sentiment,
            'reddit_highlights': match.company_insights.reddit_highlights,
            'recent_news': match.company_insights.recent_news,
            'culture_notes': match.company_insights.culture_notes,
            'data_source': match.company_insights.data_source
        },
        'match_score': match.match_score,
        'skill_overlap': match.skill_overlap,
        'skill_gaps': match.skill_gaps,
        'recommendation': match.recommendation,
        'reasoning': match.reasoning
    }


async def load_initial_data():
    """
    Load initial job matches data
    This runs a sample search to populate the API with data
    """
    global latest_matches, search_config

    print("\n" + "=" * 80)
    print("🚀 Loading initial job matches data...")
    print("=" * 80)

    # Create pipeline with mock data for faster startup
    pipeline = JobFinderPipeline(use_mock_data=True)

    # Run a sample search
    cv_path = "cvs/romCV.pdf"
    job_title = "Python Developer"
    location = "Tel Aviv"
    num_jobs = 6

    try:
        matches = await pipeline.run(
            cv_path=cv_path,
            job_title=job_title,
            location=location,
            num_jobs=num_jobs
        )

        latest_matches = matches
        search_config = {
            'role': job_title,
            'location': location,
            'cv_analyzed': True,
            'num_jobs': len(matches)
        }

        print("\n✅ Data loaded successfully!")
        print(f"   Matches: {len(matches)}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        print("   API will return empty results")
        print("=" * 80 + "\n")


def start_server(host='0.0.0.0', port=5000, load_data=True):
    """
    Start the Flask server

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 5000)
        load_data: Whether to load initial data (default: True)
    """
    if load_data:
        # Load initial data before starting server
        asyncio.run(load_initial_data())

    print("\n" + "=" * 80)
    print(f"🌐 Starting Flask API Server on http://{host}:{port}")
    print("=" * 80)
    print(f"\n📍 API Endpoints:")
    print(f"   GET  http://localhost:{port}/api/job-matches    - Get job matches")
    print(f"   GET  http://localhost:{port}/api/health         - Health check")
    print(f"   POST http://localhost:{port}/api/run-pipeline   - Run new search (not implemented)")
    print("\n" + "=" * 80 + "\n")

    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Job Finder API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--no-load', action='store_true', help='Skip loading initial data')

    args = parser.parse_args()

    start_server(host=args.host, port=args.port, load_data=not args.no_load)
