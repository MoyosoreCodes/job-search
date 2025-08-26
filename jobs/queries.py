import requests

_session = requests.Session()
_session.headers.update({'User-Agent': 'job-searcher/1.0'})

def search_serpapi(api_key: str, query: str, num: int = 20):
    params = {"engine": "google_jobs", "q": query, "api_key": api_key, "num": num}
    try:
        r = _session.get('https://serpapi.com/search', params=params, timeout=20)
        if r.status_code == 200:
            return r.json().get('jobs_results', [])
    except requests.RequestException:
        pass
    return []

def generate_queries(skills, preferences):
    queries = []
    top_skills = skills[:5]
    for skill in top_skills:
        queries.append(skill)
        if preferences.get('visa_priority', True):
            queries.append(f"{skill} visa sponsorship")
            queries.append(f"{skill} h1b")
    if preferences.get('target_countries'):
        for country in preferences['target_countries'][:2]:
            queries.append(f"software developer {country}")
    if preferences.get('remote_only'):
        queries.extend(["remote software developer", "remote backend developer"])
    return queries[:10]
