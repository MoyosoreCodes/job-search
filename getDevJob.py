# -*- coding: utf-8 -#
from __future__ import unicode_literals

import requests
import json
import pandas as pd
from datetime import datetime
import re
import os

# Please install the pdfplumber library: pip install pdfplumber
import pdfplumber

# --- CONFIGURATION ---
# Your SERPAPI Key
SERPAPI_API_KEY = "ffcf65cf29b904822ce3808351fe4d0f3af1fb4206d94702702198e6fc258cd1"

# --- IMPORTANT ---
# SET THE PATH TO YOUR CV PDF FILE HERE
CV_PDF_PATH = "C:\Users\moyos\Documents\CV\Moyosore Festus-Olaleye_Resume_Latest.pdf" 

OUTPUT_FILENAME = "found_jobs.xlsx"

# erweiterte Liste von Schlüsselwörtern
SKILLS_LIST = [
    "python", "java", "c#", ".net", "javascript", "typescript", "html", "css", "sql", "nosql",
    "react", "angular", "vue", "node.js", "express.js", "django", "flask", "spring", "ruby on rails",
    "aws", "azure", "google cloud", "docker", "kubernetes", "git", "jenkins", "ci/cd",
    "machine learning", "data science", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "agile", "scrum", "devops", "rest", "graphql", "api", "mongodb", "postgresql", "mysql",
    "software engineer", "software developer", "backend developer", "frontend developer", "fullstack developer",
    "mern stack", "mean stack", "data analyst", "systems administrator", "network engineer", "cloud engineer",
    "rust", "nextjs"
]

# --- CORE FUNCTIONS ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Error: CV file not found at '{pdf_path}'. Please update the CV_PDF_PATH variable.")
        return None
    
    print(f"Reading CV from '{pdf_path}'...")
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_skills_from_text(text, skills_list):
    """Extracts skills from text based on a predefined list."""
    found_skills = set()
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.add(skill)
    print(f"Found {len(found_skills)} skills in your CV: {', '.join(found_skills)}")
    return list(found_skills)

def get_glassdoor_link(company_name):
    if not company_name:
        return "Unknown"
    safe_name = company_name.replace(" ", "-")
    return f"https://www.glassdoor.com/Reviews/{safe_name}-Reviews-E.htm"

def contains_skills_from_cv(description, skills):
    """Checks if the job description contains any of the skills from the CV."""
    if not description or not skills:
        return False
    description_lower = description.lower()
    for skill in skills:
        if skill in description_lower:
            return True
    return False

def extract_job_link(job):
    """Extracts the most likely application link from the job data."""
    if job.get("apply_options"):
        return job["apply_options"][0].get("link")
    return job.get("link", "Not available")

def search_jobs_on_serpapi(query):
    """Queries SerpAPI for a given job search query."""
    print(f"Querying SerpAPI for '{query}'...")
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_API_KEY,
    }
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code != 200:
        print(f"Error from SerpAPI: {response.text}")
        return []
    return response.json().get("jobs_results", [])

def filter_and_format_jobs(jobs, query, skills_from_cv):
    """Filters jobs based on CV skills and formats them for output."""
    results = []
    for job in jobs:
        description = job.get("description", "")
        if not contains_skills_from_cv(description, skills_from_cv):
            continue

        job_info = {
            "Search Query": query,
            "Job Title": job.get("title"),
            "Company": job.get("company_name"),
            "Location": job.get("location"),
            "Salary": job.get("detected_extensions", {}).get("salary", "Not specified"),
            "Posting Date": job.get("detected_extensions", {}).get("posted_at", "Unknown"),
            "Job Description": description,
            "Application Link": extract_job_link(job),
            "Job Site": job.get('link', ''),
            "Glassdoor Link": get_glassdoor_link(job.get("company_name")),
        }
        results.append(job_info)
    return results

def safe_output_filename(base_filename):
    """Ensures the output filename is unique to avoid overwriting."""
    if not os.path.exists(base_filename):
        return base_filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(base_filename)
    return f"{name}_{timestamp}{ext}"

def main():
    """Main function to run the job search process."""
    cv_text = extract_text_from_pdf(CV_PDF_PATH)
    if not cv_text:
        return

    skills_from_cv = extract_skills_from_text(cv_text, SKILLS_LIST)
    if not skills_from_cv:
        print("No relevant skills found in the CV. Please check the SKILLS_LIST or your CV content.")
        return

    print("\nStarting job search based on the skills found in your CV...")
    all_jobs_filtered = []

    for skill_query in skills_from_cv:
        jobs_raw = search_jobs_on_serpapi(skill_query)
        jobs_filtered = filter_and_format_jobs(jobs_raw, skill_query, skills_from_cv)
        all_jobs_filtered.extend(jobs_filtered)

    if not all_jobs_filtered:
        print("No matching jobs found based on the skills from your CV.")
        return

    df = pd.DataFrame(all_jobs_filtered)
    df.sort_values(by="Posting Date", ascending=False, inplace=True)
    
    # Remove duplicate jobs based on title and company
    df.drop_duplicates(subset=["Job Title", "Company"], keep='first', inplace=True)

    output_filename = safe_output_filename(OUTPUT_FILENAME)
    df.to_excel(output_filename, index=False, engine='openpyxl')

    print(f"\nFound {len(df)} unique jobs. Results saved to '{output_filename}'.")

if __name__ == "__main__":
    main()