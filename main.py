import sys
from config.config import AppConfig
from cv.cv_processor import CVProcessor
from jobs.job_searcher import JobSearcher
from jobs.queries import QueryBuilder
from jobs.scoring import JobScorer
from letters.cover_letter_generator import CoverLetterGenerator
from storage.excel_handler import ExcelHandler
from storage.file_utils import FileUtils


class JobSearchApp:
    def __init__(self):
        self.config = AppConfig()
        self.cv_processor = CVProcessor()
        self.job_searcher = JobSearcher(self._get_serpapi_key())
        self.query_builder = QueryBuilder()
        self.excel_handler = ExcelHandler(self.config.RESULTS_DIR)
        self.cover_letter_generator = CoverLetterGenerator(self._get_openai_key())
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

    def _parse_preferences(self, raw_input: str) -> list[int]:
        """Parse user input like '1-3,5' into a list of integers [1,2,3,5]."""
        parts = raw_input.replace(" ", "").split(",")
        preferences = set()
        for part in parts:
            if "-" in part:
                start, end = part.split("-")
                preferences.update(range(int(start), int(end) + 1))
            else:
                preferences.add(int(part))
        return sorted(preferences)

    def run(self):
        print("AI-Powered Job Search")

        # Step 1: Load CV and extract skills
        cv_path = self._get_cv_path()
        skills = self.cv_processor.extract_skills(cv_path)
        print(f"Extracted skills: {', '.join(skills)}")

        # Step 2: Ask user for job preferences
        print("\nChoose your job priorities (you can select multiple):")
        print("1. Skill match priority")
        print("2. Visa sponsorship priority")
        print("3. Location priority")
        print("4. Remote work priority")
        print("5. Salary priority")
        pref_input = "1,2,3,4,5"
        preferences = self._parse_preferences(pref_input)
        print(f"Preferences selected: {preferences}")

        # Step 3: Build query and search jobs
        query = self.query_builder.build(skills)
        jobs = self.job_searcher.search(query)

        # Step 4: Score jobs based on chosen preferences
        scorer = JobScorer(preferences)
        scored_jobs = scorer.score_jobs(jobs, skills)

        # Step 5: Save to Excel
        excel_file = self.excel_handler.write(scored_jobs)
        print(f"Results saved to {excel_file}")

        # Step 6: Generate cover letters
        for idx, job in enumerate(scored_jobs, start=1):
            cover_letter = self.cover_letter_generator.generate(job, skills)
            filepath = self.file_utils.save_cover_letter(job["title"], idx, cover_letter)
            print(f"Cover letter saved: {filepath}")


if __name__ == "__main__":
    app = JobSearchApp()
    try:
        app.run()
    except KeyboardInterrupt:
        sys.exit("\nProcess interrupted by user")
