from urllib.parse import quote

VISA_KEYWORDS = [
    "visa sponsorship", "h1b", "work visa", "sponsor visa",
    "immigration support", "work authorization", "visa support"
]
SPONSOR_LOCATIONS = [
    "united states", "usa", "canada", "germany", "netherlands",
    "ireland", "australia", "uk", "singapore"
]

def has_visa_indicators(job):
    text = " ".join(str(job.get(field, "")) for field in ['description', 'title', 'company_name']).lower()
    for keyword in VISA_KEYWORDS:
        if keyword in text:
            return True, keyword
    return False, None

def is_sponsor_friendly(location):
    if not location:
        return False
    location_lower = location.lower()
    return any(country in location_lower for country in SPONSOR_LOCATIONS)

def calculate_score(job, skills, preferences):
    score = 0
    reasons = []
    text = (job.get('description', '') + " " + job.get('title', '')).lower()
    skill_matches = sum(1 for skill in skills if skill.lower() in text)
    if skill_matches > 0:
        score += skill_matches * 10
        reasons.append(f"{skill_matches} skill matches")

    if preferences.get('visa_priority', True):
        has_visa, keyword = has_visa_indicators(job)
        if has_visa:
            score += 100
            reasons.append(f"Visa sponsorship: {keyword}")
        elif is_sponsor_friendly(job.get('location')):
            score += 50
            reasons.append("Sponsor-friendly location")

    if preferences.get('target_countries'):
        location = job.get('location', '').lower()
        for country in preferences['target_countries']:
            if country in location:
                score += 75
                reasons.append(f"Target country: {country}")
                break

    if preferences.get('remote_only'):
        if any(term in text for term in ['remote', 'work from home']):
            score += 30
            reasons.append("Remote work")

    return score, reasons

def format_job(job, query, score, reasons):
    has_visa, _ = has_visa_indicators(job)
    visa_status = ("Yes" if has_visa else "Maybe" if is_sponsor_friendly(job.get('location')) else "Unknown")
    desc = job.get('description', '')
    short_desc = (desc[:500] + "...") if len(desc) > 500 else desc
    company = job.get('company_name', '') or 'Not specified'
    app_link = (job.get('apply_options', [{}])[0].get('link') if job.get('apply_options') else job.get('link')) or 'Not available'
    return {
        "Search Query": query,
        "Relevance Score": score,
        "Score Reasons": "; ".join(reasons),
        "Job Title": job.get("title", "Not specified"),
        "Company": company,
        "Location": job.get("location", "Not specified"),
        "Salary": job.get("detected_extensions", {}).get("salary", "Not specified"),
        "Job Description": short_desc,
        "Application Link": app_link,
        "Visa Sponsorship Mentioned": visa_status,
        "Company Glassdoor": f"https://www.glassdoor.com/Reviews/company-reviews.htm?typedKeyword={quote(company)}" if company else "Not available",
        "Application Status": "Not Applied",
        "Cover Letter Generated": "No"
    }
