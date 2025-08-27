from typing import List, Dict
import requests

class JobSearcher:
    def __init__(self, serpapi_key: str):
        self.key = serpapi_key

    def search(self, query: str, location_filter: str = None) -> List[Dict]:
        """Enhanced job search with optional location filtering."""
        print(f"Searching for: '{query}'...")
        
        params = {
            "engine": "google_jobs",
            "q": query,
            "api_key": self.key,
            "num": 20  # Get more results per query
        }
        
        if location_filter:
            params["location"] = location_filter
        
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            if response.status_code != 200:
                print(f"Error from SerpAPI: {response.text}")
                return []
            
            data = response.json()
            return data.get("jobs_results", [])
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
