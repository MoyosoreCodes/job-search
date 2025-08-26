from .queries import generate_queries, search_serpapi
from .scoring import calculate_score, format_job

class JobSearcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def search_jobs(self, skills, preferences):
        queries = generate_queries(skills, preferences)
        all_jobs = []
        seen_jobs = set()
        for query in queries:
            jobs_raw = search_serpapi(self.api_key, query)
            for job in jobs_raw:
                job_id = f"{job.get('title','')}-{job.get('company_name','')}"
                if job_id in seen_jobs:
                    continue
                seen_jobs.add(job_id)
                score, reasons = calculate_score(job, skills, preferences)
                if score <= 0:
                    continue
                formatted_job = format_job(job, query, score, reasons)
                all_jobs.append(formatted_job)
        return sorted(all_jobs, key=lambda x: x['Relevance Score'], reverse=True)
