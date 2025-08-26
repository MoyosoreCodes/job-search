# config/config.py
class Config:
    def __init__(self):
        from dotenv import load_dotenv
        import os
        load_dotenv()
        self.visa_keywords = [
            "visa sponsorship", "h1b", "work visa", "sponsor visa",
            "immigration support", "work authorization", "eligible to work",
            "visa support", "sponsorship available", "h1b visa", "work permit"
        ]
        self.sponsor_friendly = [
            "united states", "usa", "canada", "germany", "netherlands",
            "ireland", "australia", "new zealand", "uk", "singapore"
        ]
        self.os = __import__('os')

    def get_api_keys(self):
        serpapi_key = self.os.getenv('SERPAPI_KEY') or self.os.getenv('SERP_API_KEY')
        if not serpapi_key:
            serpapi_key = input("Enter your SerpAPI key: ").strip()
            if not serpapi_key:
                print("SerpAPI key is required.")
                return {'serpapi_key': None, 'openai_key': None, 'cv_path': None}

        openai_key = self.os.getenv('OPENAI_API_KEY') or input("Enter OpenAI key (or press Enter to skip): ").strip()

        cv_path = self.os.getenv('CV_PATH') or self.os.getenv('CV_FILE_PATH')
        if not cv_path or not self.os.path.exists(cv_path):
            cv_path = input("Enter path to your CV PDF: ").strip()
            if not self.os.path.exists(cv_path):
                print(f"File not found: {cv_path}")
                return {'serpapi_key': None, 'openai_key': None, 'cv_path': None}

        return {'serpapi_key': serpapi_key, 'openai_key': openai_key, 'cv_path': cv_path}

    def get_user_preferences(self):
        choice = input("Select priority (1-4, default: 1): ").strip()
        prefs = {"visa_priority": True, "target_countries": [], "remote_only": False, "skill_focus": []}
        if choice == "2":
            countries = input("Target countries (comma-separated): ").strip()
            prefs["target_countries"] = [c.strip().lower() for c in countries.split(",") if c.strip()]
        elif choice == "3":
            prefs["remote_only"] = True
        elif choice == "4":
            skills = input("Focus skills (comma-separated): ").strip()
            prefs["skill_focus"] = [s.strip().lower() for s in skills.split(",") if s.strip()]
        return prefs
