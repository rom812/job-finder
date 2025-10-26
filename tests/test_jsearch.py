"""
Quick test to verify JSearch API is working
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_jsearch_api():
    """Test JSearch API connection"""
    print("🔍 Testing JSearch API...\n")

    # Get API credentials
    api_key = os.getenv("JSEARCH_API_KEY")
    api_host = os.getenv("RAPIDAPI_HOST")

    if not api_key:
        print("❌ JSEARCH_API_KEY not found in .env file!")
        return False

    print(f"✅ API Key found: {api_key[:20]}...")
    print(f"✅ API Host: {api_host}\n")

    # Make API request
    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }

    params = {
        "query": "Python developer in Tel Aviv",
        "page": "1",
        "num_pages": "1",
        "date_posted": "all"
    }

    print("📡 Making API request...")
    print(f"   Query: {params['query']}\n")

    try:
        response = requests.get(url, headers=headers, params=params)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])

            print(f"✅ Success! Found {len(jobs)} jobs\n")

            if jobs:
                print("🎯 First job example:")
                job = jobs[0]
                print(f"   Title: {job.get('job_title')}")
                print(f"   Company: {job.get('employer_name')}")
                print(f"   Location: {job.get('job_city')}, {job.get('job_country')}")
                print(f"   Posted: {job.get('job_posted_at_datetime_utc', 'N/A')}")
                print(f"   URL: {job.get('job_apply_link', 'N/A')[:50]}...")

            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_jsearch_api()

    if success:
        print("\n" + "="*50)
        print("🎉 JSearch API is working perfectly!")
        print("✅ Ready to implement Job Scraper agent!")
    else:
        print("\n" + "="*50)
        print("❌ JSearch API test failed")
        print("Please check your API key and try again")
