import sys
import re
from urllib.parse import quote
from config.config import AppConfig
from cv.cv_processor import CVProcessor
from jobs.job_searcher import JobSearcher
from jobs.queries import QueryBuilder
from jobs.scoring import JobScorer
from letters.cover_letter_generator import CoverLetterGenerator
from storage.excel_handler import ExcelHandler
from storage.file_utils import FileUtils
from datetime import datetime
import pandas as pd

class JobSearchApp:
    def __init__(self):
        self.config = AppConfig()
        self.cv_processor = CVProcessor()
        self.job_searcher = JobSearcher(self._get_serpapi_key())
        self.query_builder = QueryBuilder()
        self.excel_handler = ExcelHandler(self.config.RESULTS_DIR)
        # self.cover_letter_generator = CoverLetterGenerator(self._get_openai_key())
        self.file_utils = FileUtils()

    def _get_serpapi_key(self) -> str:
        key = self.config.serpapi_key()
        if not key:
            key = input("Enter your SerpAPI key: ").strip()
        return key

    def _get_openai_key(self) -> str:
        key = self.config.openai_key()
        if not key:
            key = input("Enter your OpenAI API key: ").strip()
        return key

    def _get_cv_path(self) -> str:
        path = self.config.cv_path()
        if not path:
            path = input("Enter path to your CV file: ").strip()
        return path

    def _get_job_title(self) -> str:
        title = input("\nEnter the job title you are looking for (e.g., 'Software Engineer', 'Data Scientist'): ").strip()
        return title

    def _get_user_preferences(self):
        """Get user preferences for job search prioritization, allowing multiple selections."""
        print("\n=== JOB SEARCH PREFERENCES ===")
        print("1. Prioritize visa sponsorship opportunities")
        print("2. Focus on specific countries/regions")
        print("3. Prioritize remote work opportunities")
        print("4. Focus on specific skill sets")
        
        choices_input = input("\nSelect your priorities (comma-separated, e.g., 1,3): ").strip()
        choices = [c.strip() for c in choices_input.split(',') if c.strip()]
        
        all_preferences = []

        if not choices: # Default to visa sponsorship if no choice is made
            choices = ['1']

        for choice in choices:
            preferences = {
                "visa_priority": False,
                "target_countries": [],
                "remote_only": False,
                "skill_focus": []
            }

            if choice == "1":
                preferences["visa_priority"] = True
                print("Prioritizing visa sponsorship opportunities.")
            elif choice == "2":
                countries = input("Enter target countries (comma-separated): ").strip()
                preferences["target_countries"] = [c.strip().lower() for c in countries.split(",") if c.strip()]
                print(f"Focusing on countries: {', '.join(preferences['target_countries'])}")
            elif choice == "3":
                preferences["remote_only"] = True
                print("Prioritizing remote work opportunities.")
            elif choice == "4":
                skills = input("Enter skills to focus on (comma-separated): ").strip()
                preferences["skill_focus"] = [s.strip().lower() for s in skills.split(",") if s.strip()]
                print(f"Focusing on skills: {', '.join(preferences['skill_focus'])}")
            else:
                print(f"Invalid choice: {choice}. Skipping.")
                continue
            
            all_preferences.append(preferences)
        
        return all_preferences

    def _extract_job_link(self, job):
        """Extract the most relevant application link."""
        if job.get("apply_options"):
            return job["apply_options"][0].get("link", "Not available")
        return job.get("link", "Not available")

    def _get_glassdoor_link(self, company_name):
        """Generate Glassdoor search link for company research."""
        if not company_name:
            return "Not available"
        
        clean_name = company_name.strip()
        clean_name = re.sub(r'\s*(Inc\\.?|LLC\\.?|Corp\\.?|Corporation|Ltd\\.?|Limited|Co\\.?|GmbH)(\s|$)', '', clean_name, flags=re.IGNORECASE)
        
        encoded_name = quote(clean_name.strip())
        
        search_url = f"https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={encoded_name}"
        return search_url

    def _format_job_data(self, job, query, score, score_reasons, scorer):
        """Format job data for output with enhanced fields."""
        has_visa, _ = scorer.has_visa_sponsorship_indicators(job)
        sponsorship_mentioned = "Yes" if has_visa else "Maybe" if scorer.is_sponsor_friendly_location(job.get('location')) else "Unknown"

        return {
            "Search Query": query,
            "Relevance Score": score,
            "Score Reasons": "; ".join(score_reasons),
            "Job Title": job.get("title", "Not specified"),
            "Company": job.get("company_name", "Not specified"),
            "Location": job.get("location", "Not specified"),
            "Salary": job.get("detected_extensions", {}).get("salary", "Not specified"),
            "Posting Date": job.get("detected_extensions", {}).get("posted_at", "Unknown"),
            "Job Description": job.get("description", "")[:500] + "..." if len(job.get("description", "")) > 500 else job.get("description", ""),
            "Application Link": self._extract_job_link(job),
            "Visa Sponsorship Mentioned": sponsorship_mentioned,
            "Company Glassdoor": self._get_glassdoor_link(job.get("company_name"))
        }

    def run(self):
        print("AI-Powered Job Search")

        cv_path = self._get_cv_path()
        skills = self.cv_processor.extract_skills(cv_path)
        print(f"Extracted skills: {', '.join(skills)}")
        job_title = input("Enter job title (Software engineer, Data analyst): ")

        list_of_preferences = self._get_user_preferences() # Now returns a list of preferences
        
        all_jobs = []
        seen_jobs = set()

        for preferences in list_of_preferences: # Loop through each preference set
            scorer = JobScorer(preferences) # Initialize scorer for each preference set

            print(f"\nSearching for jobs based on your preferences...")
            print(f"Skills found: {len(skills)}")
            print(f"Visa priority: {'Yes' if preferences.get('visa_priority') else 'No'}")

            target_countries = preferences.get("target_countries", [])
            
            if not target_countries:
                # If no specific target countries, build queries without a specific target country
                search_queries = self.query_builder.build(skills, job_title=job_title)
            else:
                # Build queries for each specified target country
                search_queries = []
                for country in target_countries:
                    search_queries.extend(self.query_builder.build(skills, job_title=job_title, target_country=country))

            # Deduplicate queries after combining from multiple target countries
            search_queries = list(set(search_queries))

            for query in search_queries:
                jobs_raw = self.job_searcher.search(query)
                
                for job in jobs_raw:
                    job_id = f"{job.get('title', '')}-{job.get('company_name', '')}-{job.get('location', '')}"
                    if job_id in seen_jobs:
                        continue
                    seen_jobs.add(job_id)
                    
                    score, score_reasons = scorer.calculate_job_score(job, skills)
                    
                    if score > 0:
                        formatted_job = self._format_job_data(job, query, score, score_reasons, scorer)
                        all_jobs.append(formatted_job)

        if not all_jobs:
            print("No matching jobs found. Try adjusting your preferences or CV skills.")
            return

        df = pd.DataFrame(all_jobs)
        df = df.sort_values(['Relevance Score', 'Posting Date'], ascending=[False, False])

        excel_file = self.excel_handler.write(df.to_dict('records'))
        print(f"\nResults saved to {excel_file}")

        print(f"\n=== TOP 5 MATCHES ===")
        for idx, row in df.head().iterrows():
            print(f"\n{idx+1}. {row['Job Title']} at {row['Company']}")
            print(f"   Location: {row['Location']}")
            print(f"   Score: {row['Relevance Score']} ({row['Score Reasons']})")
            print(f"   Visa Sponsorship: {row['Visa Sponsorship Mentioned']}")

if __name__ == "__main__":
    app = JobSearchApp()
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit("\nProcess interrupted by user")
