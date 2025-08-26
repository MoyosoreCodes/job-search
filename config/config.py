from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    RESULTS_DIR = Path("job_search_results")
    COVER_LETTER_DIR = RESULTS_DIR / "cover_letters"
    SHEET_NAME = "Job Search Results"
    APPLICATION_STATUS_OPTIONS = ["Not Applied", "Applied", "Interviewing", "Offered", "Rejected"]

    @staticmethod
    def serpapi_key() -> str:
        return os.getenv("SERPAPI_KEY", "").strip()

    @staticmethod
    def openai_key() -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    @staticmethod
    def cv_path() -> str:
        return os.getenv("CV_PATH", "").strip()

    @staticmethod
    def target_country() -> str:
        return os.getenv("TARGET_COUNTRY", "").strip()

