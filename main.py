# main.py
from config.config import Config
from cv.cv_processor import CVProcessor
from jobs.job_searcher import JobSearcher
from letters.cover_letter_generator import CoverLetterGenerator
from storage.excel_handler import ExcelHandler
from storage.file_utils import create_results_folder


def main():
    print("=== AI-Powered Job Search with Visa Sponsorship Priority ===\n")

    config = Config()
    api_keys = config.get_api_keys()
    if not api_keys['serpapi_key'] or not api_keys['cv_path']:
        return

    cv_processor = CVProcessor(api_keys['cv_path'])
    cv_text = cv_processor.extract_text()
    if not cv_text:
        return

    section_headers = cv_processor.get_section_headers()
    resume_data = cv_processor.extract_all_sections(cv_text, section_headers)
    if not resume_data['skills']:
        print("No valid skills confirmed. Exiting...")
        return

    preferences = config.get_user_preferences()

    job_searcher = JobSearcher(api_keys['serpapi_key'])
    jobs_data = job_searcher.search_jobs(resume_data['skills'], preferences)
    if not jobs_data:
        print("No matching jobs found. Try adjusting your preferences or CV skills.")
        return

    results_folder = create_results_folder()

    cover_letter_count = 0
    if api_keys['openai_key']:
        generate_letters = input("Generate cover letters for top jobs? (y/n, default: n): ").strip().lower() in ['y', 'yes']
        if generate_letters:
            max_letters = min(int(input("How many? (default: 5, max: 10): ").strip() or "5"), 10)
            cl_generator = CoverLetterGenerator(api_keys['openai_key'])
            cover_letter_count = cl_generator.generate_multiple(
                jobs_data[:max_letters], resume_data, results_folder
            )

    excel_handler = ExcelHandler()
    output_path = excel_handler.save_results(jobs_data, results_folder)

    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total jobs found: {len(jobs_data)}")
    print(f"Jobs with explicit visa sponsorship: {sum(1 for job in jobs_data if job['Visa Sponsorship Mentioned'] == 'Yes')}")
    print(f"Cover letters generated: {cover_letter_count}")
    print(f"Results saved to: {output_path}")

    print(f"\n=== TOP 5 MATCHES ===")
    for i, job in enumerate(jobs_data[:5], 1):
        print(f"\n{i}. {job['Job Title']} at {job['Company']}")
        print(f"   Score: {job['Relevance Score']} - {job['Location']}")
        print(f"   Visa: {job['Visa Sponsorship Mentioned']}")


if __name__ == "__main__":
    main()