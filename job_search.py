# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import re
import os
from collections import Counter
from urllib.parse import quote

# Please install the pdfplumber library: pip install pdfplumber
import pdfplumber

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION ---
OUTPUT_FILENAME = "job_search_results.xlsx"


def normalize_posting_date(raw: str) -> datetime:
    """Convert any SerpAPI date string to a datetime for reliable sorting.

    Handles: 'today', 'N days/hours/weeks/months ago',
             'YYYY-MM-DD', 'Month DD, YYYY'.
    Returns datetime.min on unrecognised input so unknown dates sort last.
    """
    if not raw or str(raw).strip() in ("Unknown", "Not specified", ""):
        return datetime.min

    s = str(raw).strip().lower()

    if s in ("today", "just now"):
        return datetime.now()
    if s in ("yesterday", "1 day ago"):
        return datetime.now() - timedelta(days=1)

    m = re.match(r"(\d+)\s+day", s)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)))
    m = re.match(r"(\d+)\s+hour", s)
    if m:
        return datetime.now() - timedelta(hours=int(m.group(1)))
    m = re.match(r"(\d+)\s+week", s)
    if m:
        return datetime.now() - timedelta(weeks=int(m.group(1)))
    m = re.match(r"(\d+)\s+month", s)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)) * 30)

    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue

    return datetime.min

def get_user_configuration():
    """Get API key and CV path from environment variables first, then user input."""
    print("=== INITIAL SETUP ===")
    
    # Try to get SerpAPI key from environment variables first
    api_key = os.getenv('SERPAPI_KEY') or os.getenv('SERP_API_KEY')
    
    if api_key:
        print(f"✅ Found SerpAPI key in environment variables: {api_key[:8]}...")
    else:
        print("\n1. SerpAPI Key Required")
        print("   - Visit: https://serpapi.com/")
        print("   - Sign up for a free account")
        print("   - Get your API key from the dashboard")
        print("   - You can also add it to your .env file as SERPAPI_KEY=your_key_here")
        
        api_key = input("\nEnter your SerpAPI key: ").strip()
        if not api_key:
            print("❌ API key is required to search for jobs.")
            return None, None
    
    # Try to get CV path from environment variables first
    cv_path = os.getenv('CV_PATH') or os.getenv('CV_FILE_PATH')
    
    if cv_path:
        print(f"✅ Found CV path in environment variables: {cv_path}")
        # Validate file exists
        if not os.path.exists(cv_path):
            print(f"❌ CV file not found at environment path: {cv_path}")
            print("Please update your .env file or provide a new path.")
            cv_path = None
    
    if not cv_path:
        print("\n2. CV File Path")
        print("   - Provide the full path to your CV PDF file")
        print("   - Example: C:\\Users\\username\\Documents\\my_cv.pdf")
        print("   - Or: /Users/username/Documents/my_cv.pdf (Mac/Linux)")
        print("   - You can also add it to your .env file as CV_PATH=path/to/your/cv.pdf")
        
        cv_path = input("\nEnter the path to your CV PDF file: ").strip()
        if not cv_path:
            print("❌ CV file path is required.")
            return None, None
        
        # Validate file exists
        if not os.path.exists(cv_path):
            print(f"❌ File not found at: {cv_path}")
            print("Please check the path and try again.")
            return None, None
    
    print(f"✅ Configuration complete!")
    print(f"   API Key: {api_key[:8]}...")
    print(f"   CV File: {cv_path}")
    
    return api_key, cv_path

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

COUNTRIES = [
    "United States", "Canada", "Germany", "Netherlands", "Ireland", "Australia", "New Zealand", "United Kingdom", "Sweden", "Denmark", "Switzerland", "Austria", "Singapore", "France", "Spain", "Italy", "Japan", "China", "India", "Brazil", "Mexico"
]

# --- CORE FUNCTIONS ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Error: CV file not found at '{pdf_path}'. Please update the CV_PDF_PATH variable.")
        return None
    
    print(f"Reading CV from '{pdf_path}'...")
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "".join(pages)

def get_skills_section_from_user():
    """Ask user which section contains their skills."""
    print("\n=== SKILLS SECTION IDENTIFICATION ===")
    print("To extract your skills accurately, please specify which section contains your skills.")
    print("Common section names: 'Skills', 'Technical Skills', 'Core Competencies', 'Technologies', etc.")
    print("If unsure, just press Enter to use 'Skills' as default.")
    
    section_name = input("\nEnter the name of your skills section (default: 'Skills'): ").strip()
    
    if not section_name:
        section_name = "Skills"
    
    print(f"Will extract skills from the '{section_name}' section.")
    return section_name

def extract_skills_from_specified_section(cv_text, section_name):
    """Extract skills from the user-specified section."""
    if not cv_text or not section_name:
        return []
    
    print(f"\nLooking for '{section_name}' section in your CV...")
    
    # Create flexible pattern to find the specified section
    section_pattern = rf'{re.escape(section_name)}\s*\n(.*?)(?=\n[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\n|\n\s*\n|\Z)'
    
    match = re.search(section_pattern, cv_text, re.IGNORECASE | re.DOTALL)
    
    if not match:
        print(f"❌ Could not find '{section_name}' section in your CV.")
        print("Available sections detected:")
        
        # Show available sections to help user
        section_headers = re.findall(r'\n([A-Z][a-z]+(?:\s+[A-Z&][a-z]*)*)\s*\n', cv_text)
        for i, header in enumerate(set(section_headers), 1):
            print(f"  {i}. {header}")
        
        return []
    
    skills_content = match.group(1).strip()
    print(f"✅ Found '{section_name}' section!")
    print(f"Raw content preview: {skills_content[:200]}...")
    
    # Extract skills from the content
    skills = extract_skills_from_content(skills_content)
    
    return skills

def extract_skills_from_content(content):
    """Extract individual skills from the skills section content."""
    skills = {}  # dict preserves insertion order; used as an ordered set
    
    # Split content into lines and process each line
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('•') and len(line) < 5:
            continue
        
        # Remove bullet points and prefixes
        line = re.sub(r'^[•\-\*]\s*', '', line)
        line = re.sub(r'^(Programming Languages?|Database|DevOps\s*[&\s]*Tools?|Technologies?|Frameworks?|Languages?)\s*[:\-]?\s*', '', line, flags=re.IGNORECASE)
        
        # Split by common delimiters
        skill_items = re.split(r'[,;]+', line)
        
        for item in skill_items:
            item = item.strip()
            # Clean up the skill name
            item = re.sub(r'^(and\s+|&\s+)', '', item, flags=re.IGNORECASE)
            item = item.strip('.,;:•-() ')
            
            # Filter valid skills (not empty, not too short/long, not common words)
            if (item and len(item) >= 2 and len(item) <= 50 and
                not re.match(r'^(the|and|or|with|using|include|includes?|etc)', item, re.IGNORECASE)):
                skills[item] = None   # key deduplicates; order preserved

    return list(skills.keys())

def extract_job_title(cv_text):
    """Extract job title from the CV text."""
    # Common job title keywords
    job_title_keywords = [
        'software engineer', 'developer', 'programmer', 'engineer', 'scientist',
        'analyst', 'manager', 'consultant', 'architect', 'specialist'
    ]
    
    # Regex to find lines that likely contain a job title
    # This looks for lines with 1-5 words, containing at least one keyword,
    # and not starting with a common section header.
    pattern = re.compile(
        r'^'
        r'(?!'
        r'(?:summary|objective|experience|education|skills|projects|awards|references)'
        r'\s*'
        r')'
        r'((?:[a-z][a-z,]+-?)+[a-z]?\s+){0,4}'
        r'(' + '|'.join(job_title_keywords) + ')'
        r'((?:\s+[a-z][a-z,]+-?)+[a-z]?){0,4}'
        r'',
        re.IGNORECASE | re.MULTILINE
    )
    
    matches = pattern.findall(cv_text)
    
    if matches:
        # The first match is often the most recent job title
        # We join the matched groups to form the full title
        return "".join(matches[0]).strip()
    
    return None

def extract_experience(cv_text):
    """Extract experience section from the CV text."""
    experience_section = None
    
    # Regex to find the experience section
    # It looks for a line starting with "Experience" and captures everything until the next section
    pattern = re.compile(r'^\s*(experience|work experience|professional experience)\s*$(.*?)^\s*(?=\w+\s*$)', re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    match = pattern.search(cv_text)
    
    if match:
        experience_section = match.group(2).strip()
        
    return experience_section

def extract_name(cv_text):
    """Extract name from the CV text."""
    # Regex to find a name at the beginning of the CV
    # Assumes the name is one of the first few lines and consists of 2-3 words
    pattern = re.compile(r'^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*',
        re.IGNORECASE | re.MULTILINE
    )
    
    match = pattern.search(cv_text)
    
    if match:
        return match.group(1).strip()
    
    return None

def validate_extracted_skills(skills):
    """Validate and confirm extracted skills with user."""
    if not skills:
        return []
    
    print(f"\n=== EXTRACTED SKILLS ===")
    print(f"Found {len(skills)} skills:")
    
    # Display skills in a readable format
    for i, skill in enumerate(skills, 1):
        print(f"  {i:2d}. {skill}")
    
    print(f"\n=== SKILL VALIDATION ===")
    confirm = input("Do these skills look correct? (y/n, default: y): ").strip().lower()
    
    if confirm in ['n', 'no']:
        print("You can either:")
        print("1. Edit your CV and restart the script")
        print("2. Manually specify skills to add/remove")
        
        action = input("Choose action (1/2, default: 1): ").strip()
        
        if action == '2':
            print("\nCurrent skills:", ", ".join(skills))
            add_skills = input("Skills to add (comma-separated, or press Enter to skip): ").strip()
            remove_skills = input("Skills to remove (comma-separated, or press Enter to skip): ").strip()
            
            if add_skills:
                new_skills = [s.strip() for s in add_skills.split(',') if s.strip()]
                skills.extend(new_skills)
                print(f"Added: {new_skills}")
            
            if remove_skills:
                remove_list = [s.strip().lower() for s in remove_skills.split(',') if s.strip()]
                skills = [s for s in skills if s.lower() not in remove_list]
                print(f"Removed skills matching: {remove_list}")
        else:
            print("Please update your CV's skills section and run the script again.")
            return []
    
    final_skills = list(dict.fromkeys(skills))  # Remove duplicates, preserve order
    print(f"\n✅ Final skills list ({len(final_skills)} skills): {', '.join(final_skills)}")
    return final_skills

def get_user_preferences():
    """Get user preferences for job search prioritization."""
    print("\n=== JOB SEARCH PREFERENCES ===")
    print("1. Prioritize visa sponsorship opportunities (default)")
    print("2. Focus on specific countries/regions")
    print("3. Prioritize remote work opportunities")
    print("4. Focus on specific skill sets")
    
    choice = input("\nSelect your priority (1-4, default is 1): ").strip()
    
    preferences = {
        "visa_priority": True,  # Default
        "target_countries": [],
        "remote_only": False,
        "skill_focus": []
    }
    
    if choice == "2":
        countries = input("Enter target countries (comma-separated): ").strip()
        preferences["target_countries"] = [c.strip().lower() for c in countries.split(",") if c.strip()]
    elif choice == "3":
        preferences["remote_only"] = True
        print("Will prioritize remote work opportunities.")
    elif choice == "4":
        skills = input("Enter skills to focus on (comma-separated): ").strip()
        preferences["skill_focus"] = [s.strip().lower() for s in skills.split(",") if s.strip()]
    
    return preferences

def has_visa_sponsorship_indicators(job_data):
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
    
    return False, None

def is_sponsor_friendly_location(location):
    """Check if location is in a visa sponsor-friendly country."""
    if not location:
        return False
    
    location_lower = location.lower()
    for country in SPONSOR_FRIENDLY_LOCATIONS:
        if country in location_lower:
            return True
    return False

def calculate_job_score(job, skills_from_cv, preferences):
    """Calculate a relevance score for each job based on preferences."""
    score = 0
    reasons = []
    
    # Base skill matching score
    description = job.get('description', '').lower()
    title = job.get('title', '').lower()
    combined_text = description + " " + title
    
    skill_matches = sum(1 for skill in skills_from_cv if skill.lower() in combined_text)
    score += skill_matches * 10
    if skill_matches > 0:
        reasons.append(f"{skill_matches} skill matches")
    
    # Visa sponsorship bonus
    if preferences.get('visa_priority', True):
        has_visa, visa_keyword = has_visa_sponsorship_indicators(job)
        if has_visa:
            score += 100  # High bonus for explicit visa sponsorship
            reasons.append(f"Visa sponsorship: {visa_keyword}")
        elif is_sponsor_friendly_location(job.get('location')):
            score += 50  # Moderate bonus for sponsor-friendly location
            reasons.append("Sponsor-friendly location")
    
    # Target countries bonus
    if preferences.get('target_countries'):
        location = job.get('location', '').lower()
        for country in preferences['target_countries']:
            if country in location:
                score += 75
                reasons.append(f"Target country: {country}")
                break
    
    # Remote work bonus
    if preferences.get('remote_only'):
        if any(term in combined_text for term in ['remote', 'work from home', 'telecommute']):
            score += 30
            reasons.append("Remote work available")
    
    # Skill focus bonus
    if preferences.get('skill_focus'):
        for focus_skill in preferences['skill_focus']:
            if focus_skill in combined_text:
                score += 25
                reasons.append(f"Focus skill: {focus_skill}")
    
    return score, reasons

def search_jobs_with_visa_focus(skills_from_cv, preferences):
    """Search for jobs with enhanced queries for visa sponsorship."""
    search_queries = []
    
    # Primary skill-based searches
    top_skills = skills_from_cv[:5]  # Focus on top 5 skills to avoid API limits
    
    for skill in top_skills:
        # Basic skill search
        search_queries.append(skill)
        
        # Visa-focused searches if prioritized
        if preferences.get('visa_priority', True):
            search_queries.append(f"{skill} visa sponsorship")
            search_queries.append(f"{skill} h1b sponsor")
    
    # Location-specific searches
    if preferences.get('target_countries'):
        for country in preferences['target_countries'][:2]:  # Limit to avoid too many queries
            search_queries.append(f"software developer {country}")
    
    # Remote work searches
    if preferences.get('remote_only'):
        search_queries.append("remote software developer")
        search_queries.append("remote backend developer")
    
    return search_queries[:10]  # Limit total queries to manage API costs

def search_jobs_on_serpapi(query, api_key, location_filter=None):
    """Enhanced job search with optional location filtering."""
    print(f"Searching for: '{query}'...")

    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": api_key,
        "num": 20  # Get more results per query
    }

    # location_filter must be a single string for SerpAPI
    if location_filter and isinstance(location_filter, str):
        params["location"] = location_filter

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)

        if response.status_code == 401:
            print("SerpAPI error: Invalid API key.")
            return []
        if response.status_code == 429:
            print("SerpAPI error: Rate limit reached. Try again in a moment.")
            return []
        if response.status_code != 200:
            print(f"SerpAPI error {response.status_code}: {response.text[:200]}")
            return []

        data = response.json()

        # SerpAPI sometimes returns HTTP 200 with an error field
        if "error" in data:
            msg = data["error"]
            print(f"SerpAPI error: {msg}")
            return []

        return data.get("jobs_results", [])

    except requests.exceptions.ConnectionError:
        print("Network error: Could not reach SerpAPI. Check your internet connection.")
        return []
    except requests.exceptions.Timeout:
        print("Request timed out while contacting SerpAPI.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []

def extract_job_link(job):
    """Extract the most relevant application link."""
    if job.get("apply_options"):
        return job["apply_options"][0].get("link", "Not available")
    return job.get("link", "Not available")

def get_glassdoor_link(company_name):
    """Generate Glassdoor search link for company research."""
    if not company_name:
        return "Not available"
    
    # Clean the company name for search
    clean_name = company_name.strip()
    # Remove common business suffixes for better search results
    clean_name = re.sub(r'\s*(Inc\\.?|LLC\\.?|Corp\\.?|Corporation|Ltd\\.?|Limited|Co\\.?)(?:\s|$)', '', clean_name, flags=re.IGNORECASE)
    
    # URL encode the company name for the search query
    encoded_name = quote(clean_name.strip())
    
    # Generate Glassdoor search URL - much more reliable than trying to guess company page URLs
    search_url = f"https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={encoded_name}"
    return search_url

def format_job_data(job, query, score, score_reasons):
    """Format job data for output with enhanced fields."""
    desc     = job.get("description", "")
    raw_date = job.get("detected_extensions", {}).get("posted_at", "Unknown")
    return {
        "Search Query":    query,
        "Relevance Score": score,
        "Score Reasons":   "; ".join(score_reasons),
        "Job Title":       job.get("title", "Not specified"),
        "Company":         job.get("company_name", "Not specified"),
        "Location":        job.get("location", "Not specified"),
        "Salary":          job.get("detected_extensions", {}).get("salary", "Not specified"),
        "Posting Date":    raw_date,
        # ISO string used by the GUI for reliable date sorting (not exported to Excel/CSV)
        "Posting Date ISO": normalize_posting_date(raw_date).isoformat(),
        # Truncated version for export; full text kept under _full_description for the GUI
        "Job Description":  desc[:500] + "..." if len(desc) > 500 else desc,
        "_full_description": desc,
        "Application Link": extract_job_link(job),
        "Visa Sponsorship Mentioned": (
            "Yes" if has_visa_sponsorship_indicators(job)[0]
            else "Maybe" if is_sponsor_friendly_location(job.get("location"))
            else "Unknown"
        ),
        "Company Glassdoor": get_glassdoor_link(job.get("company_name")),
    }

def get_default_output_folder():
    """Return the default output folder: ~/Documents/Job Search Results/"""
    documents = os.path.join(os.path.expanduser("~"), "Documents")
    return os.path.join(documents, "Job Search Results")


def create_results_folder(base_folder=None):
    """Create a date-stamped sub-folder inside *base_folder* (or the default Documents
    location) and return its absolute path."""
    if not base_folder:
        base_folder = get_default_output_folder()

    folder_name = datetime.now().strftime('%B_%d_%Y')   # e.g. "March_20_2026"
    results_folder = os.path.join(base_folder, folder_name)
    os.makedirs(results_folder, exist_ok=True)
    return results_folder

def main():
    """Enhanced main function with user preferences and better filtering."""
    print("=== AI-Powered Job Search with Visa Sponsorship Priority ===\n")
    
    # Check if .env file exists and inform user
    env_exists = os.path.exists('.env')
    if not env_exists:
        print("💡 Tip: Create a .env file in this directory with:")
        print("   SERPAPI_KEY=your_serpapi_key_here")
        print("   CV_PATH=/path/to/your/cv.pdf")
        print("   This will save you time on future runs!\n")
    
    # Get user configuration
    api_key, cv_path = get_user_configuration()
    if not api_key or not cv_path:
        return
    
    # Extract text from CV
    cv_text = extract_text_from_pdf(cv_path)
    if not cv_text:
        return
    
    # Get skills section name from user
    skills_section_name = get_skills_section_from_user()
    
    # Extract skills from the specified section
    skills_from_cv = extract_skills_from_specified_section(cv_text, skills_section_name)
    
    if not skills_from_cv:
        print("❌ No skills could be extracted. Please check your CV format or section name.")
        return
    
    # Validate extracted skills with user
    skills_from_cv = validate_extracted_skills(skills_from_cv)
    if not skills_from_cv:
        print("No valid skills confirmed. Exiting...")
        return
    
    # Get user preferences
    preferences = get_user_preferences()
    
    print(f"\nSearching for jobs based on your preferences...")
    print(f"Skills found: {len(skills_from_cv)}")
    print(f"Visa priority: {'Yes' if preferences.get('visa_priority') else 'No'}")
    
    # Generate search queries
    search_queries = search_jobs_with_visa_focus(skills_from_cv, preferences)
    
    all_jobs = []
    seen_jobs = set()  # To avoid duplicates
    
    for query in search_queries:
        jobs_raw = search_jobs_on_serpapi(query, api_key)
        
        for job in jobs_raw:
            # Create unique identifier for job
            job_id = f"{job.get('title', '')}-{job.get('company_name', '')}-{job.get('location', '')}"
            if job_id in seen_jobs:
                continue
            seen_jobs.add(job_id)
            
            # Calculate relevance score
            score, score_reasons = calculate_job_score(job, skills_from_cv, preferences)
            
            # Only include jobs with some relevance
            if score > 0:
                formatted_job = format_job_data(job, query, score, score_reasons)
                all_jobs.append(formatted_job)
    
    if not all_jobs:
        print("No matching jobs found. Try adjusting your preferences or CV skills.")
        return
    
    # Create DataFrame and sort by relevance score
    df = pd.DataFrame(all_jobs)
    df = df.sort_values(['Relevance Score', 'Posting Date'], ascending=[False, False])
    
    # Create results folder and save file
    results_folder = create_results_folder()
    output_filename = f"job_search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(results_folder, output_filename)
    
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    # Print summary
    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total jobs found: {len(df)}")
    print(f"Jobs with explicit visa sponsorship: {len(df[df['Visa Sponsorship Mentioned'] == 'Yes'])}")
    print(f"Jobs in sponsor-friendly locations: {len(df[df['Visa Sponsorship Mentioned'] == 'Maybe'])}")
    print(f"Results folder: {results_folder}")
    print(f"Results saved to: {output_path}")
    
    # Show top 5 results
    print(f"\n=== TOP 5 MATCHES ===")
    for idx, row in df.head().iterrows():
        print(f"\n{idx+1}. {row['Job Title']} at {row['Company']}")
        print(f"   Location: {row['Location']}")
        print(f"   Score: {row['Relevance Score']} ({row['Score Reasons']})")
        print(f"   Visa Sponsorship: {row['Visa Sponsorship Mentioned']}")

if __name__ == "__main__":
    main()