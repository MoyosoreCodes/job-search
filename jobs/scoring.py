from typing import List, Dict, Tuple

# Visa sponsorship keywords to prioritize
VISA_KEYWORDS = [
    "visa sponsorship", "h1b", "work visa", "sponsor visa", "immigration support",
    "work authorization", "eligible to work", "visa support", "sponsorship available",
    "h1b visa", "work permit", "visa assistance", "international candidates",
    "relocation assistance", "global talent", "overseas candidates"
]

# Countries/regions known for visa sponsorship opportunities
SPONSOR_FRIENDLY_LOCATIONS = [
    "united states", "usa", "canada", "germany", "netherlands", "ireland", 
    "australia", "new zealand", "uk", "united kingdom", "sweden", "denmark",
    "switzerland", "austria", "singapore"
]

class JobScorer:
    def __init__(self, preferences: dict):
        self.preferences = preferences

    def has_visa_sponsorship_indicators(self, job_data: Dict) -> Tuple[bool, str]:
        """Check if job posting indicates visa sponsorship availability."""
        text_to_check = ""
        
        # Combine relevant job fields for checking
        for field in ['description', 'title', 'company_name']:
            if job_data.get(field):
                text_to_check += " " + str(job_data[field])
        
        text_to_check = text_to_check.lower()
        
        # Check for visa sponsorship keywords
        for keyword in VISA_KEYWORDS:
            if keyword in text_to_check:
                return True, keyword
        
        return False, ""

    def is_sponsor_friendly_location(self, location: str) -> bool:
        """Check if location is in a visa sponsor-friendly country."""
        if not location:
            return False
        
        location_lower = location.lower()
        for country in SPONSOR_FRIENDLY_LOCATIONS:
            if country in location_lower:
                return True
        return False

    def calculate_job_score(self, job: Dict, skills_from_cv: List[str]) -> Tuple[int, List[str]]:
        """Calculate a relevance score for each job based on preferences."""
        score = 0
        reasons = []
        
        description = job.get('description', '').lower()
        title = job.get('title', '').lower()
        combined_text = description + " " + title
        
        skill_matches = sum(1 for skill in skills_from_cv if skill.lower() in combined_text)
        if skill_matches > 0:
            score += skill_matches * 10
            reasons.append(f"{skill_matches} skill matches")
        
        if self.preferences.get('visa_priority'):
            has_visa, visa_keyword = self.has_visa_sponsorship_indicators(job)
            if has_visa:
                score += 100
                reasons.append(f"Visa sponsorship: {visa_keyword}")
            elif self.is_sponsor_friendly_location(job.get('location')):
                score += 50
                reasons.append("Sponsor-friendly location")
        
        if self.preferences.get('target_countries'):
            location = job.get('location', '').lower()
            for country in self.preferences['target_countries']:
                if country in location:
                    score += 75
                    reasons.append(f"Target country: {country}")
                    break
        
        if self.preferences.get('remote_only'):
            if any(term in combined_text for term in ['remote', 'work from home', 'telecommute']):
                score += 30
                reasons.append("Remote work available")
        
        if self.preferences.get('skill_focus'):
            for focus_skill in self.preferences['skill_focus']:
                if focus_skill in combined_text:
                    score += 25
                    reasons.append(f"Focus skill: {focus_skill}")
        
        return score, reasons
