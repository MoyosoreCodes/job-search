class JobScorer:
    def __init__(self, preferences: list[int]):
        self.preferences = preferences

    def _skill_match_score(self, job, skills):
        job_desc = (job.get("description") or "").lower()
        matches = sum(1 for skill in skills if skill.lower() in job_desc)
        return matches * 10

    def _visa_sponsorship_score(self, job):
        text = (job.get("description") or "").lower()
        if "visa sponsorship" in text or "work visa" in text:
            return 100
        return 0

    def _location_score(self, job):
        location = (job.get("location") or "").lower()
        preferred_location = "united kingdom"
        return 75 if preferred_location in location else 0

    def _remote_score(self, job):
        text = (job.get("description") or "").lower()
        if "remote" in text or "work from home" in text:
            return 50
        return 0

    def _salary_score(self, job):
        salary = job.get("salary")
        if not salary:
            return 0
        try:
            value = int("".join(filter(str.isdigit, str(salary))))
            if value > 60000:
                return 40
        except ValueError:
            pass
        return 0

    def score_jobs(self, jobs: list[dict], skills: list[str]) -> list[dict]:
        scored = []
        for job in jobs:
            score = 0
            if 1 in self.preferences:
                score += self._skill_match_score(job, skills)
            if 2 in self.preferences:
                score += self._visa_sponsorship_score(job)
            if 3 in self.preferences:
                score += self._location_score(job)
            if 4 in self.preferences:
                score += self._remote_score(job)
            if 5 in self.preferences:
                score += self._salary_score(job)

            job["score"] = score
            scored.append(job)

        return sorted(scored, key=lambda j: j["score"], reverse=True)
