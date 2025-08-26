from typing import List, Dict
import requests

class JobSearcher:
    def __init__(self, serpapi_key: str):
        self.key = serpapi_key

    def search(self, queries: List[str], limit: int = 30) -> List[Dict]:
        results: List[Dict] = []
        for q in queries:
            payload = {
                "engine": "google_jobs",
                "q": q,
                "hl": "en",
                "api_key": self.key
            }
            try:
                r = requests.get("https://serpapi.com/search.json", params=payload, timeout=30)
                data = r.json()
                jobs = data.get("jobs_results", []) if isinstance(data, dict) else []
                for j in jobs:
                    results.append(self._map_job(j))
                    if len(results) >= limit:
                        return results
            except Exception:
                continue
        return results

    def _map_job(self, j: Dict) -> Dict:
        return {
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("location", ""),
            "salary": j.get("detected_extensions", {}).get("salary", ""),
            "short_description": j.get("description", "")[:500],
            "application_link": self._first_link(j),
            "visa_status": "",
            "company_glassdoor_link": ""
        }

    def _first_link(self, j: Dict) -> str:
        links = j.get("related_links") or []
        if links and isinstance(links, list):
            return links[0].get("link", "") or ""
        return j.get("apply_options", [{}])[0].get("link", "") if isinstance(j.get("apply_options"), list) else ""
