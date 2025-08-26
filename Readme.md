# 🚀 AI-Powered Job Search with Visa Sponsorship Priority

An automated job search tool that extracts skills from a PDF CV, searches for relevant roles with visa sponsorship signals, scores results, and exports an Excel report. Optional cover letter generation via OpenAI.

## Project layout

project_root/
├── main.py
├── config/
│   └── config.py
├── cv/
│   └── cv_processor.py
├── jobs/
│   ├── job_searcher.py
│   ├── queries.py
│   └── scoring.py
├── letters/
│   └── cover_letter_generator.py
├── storage/
│   ├── excel_handler.py
│   └── file_utils.py
├── utils/
│   └── common.py
└── requirements.txt

## Requirements

- Python 3.9 or later
- Internet access for SerpAPI and OpenAI calls
- A text-based PDF CV, not a scanned image
- SerpAPI key (required)
- OpenAI key (optional, required only for cover letter generation)
- Python packages listed in requirements.txt:
  - pdfplumber
  - requests
  - python-dotenv
  - openai
  - python-docx
  - pandas
  - openpyxl

## Quick install

From project root:

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

If you prefer manual installs:

pip install pdfplumber requests python-dotenv openai python-docx pandas openpyxl

## Configuration

Use a .env file or environment variables. Example .env:

SERPAPI_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_key_here   # optional
CV_PATH=/full/path/to/your_cv.pdf

Or set env vars inline for a one-off run:

Unix / macOS:
export SERPAPI_KEY="xxx"
export OPENAI_API_KEY="yyy"   # optional
export CV_PATH="/path/to/cv.pdf"
python main.py

Windows PowerShell:
$env:SERPAPI_KEY="xxx"
$env:OPENAI_API_KEY="yyy"
$env:CV_PATH="C:\path\to\cv.pdf"
python main.py

## How to run

From project root:
python main.py

The script is interactive, it will prompt for any missing keys, CV path, section headers, and search preferences. If OPENAI_API_KEY is present, you will be prompted whether to generate cover letters.

### Non-interactive run

Set required env vars then run, this skips supplying keys interactively:

SERPAPI_KEY="xxx" OPENAI_API_KEY="yyy" CV_PATH="/path/to/cv.pdf" python main.py

On Windows, set env vars as shown above before running python main.py.

## Outputs

- Results folder: job_search_results/<Month_Day_Year>/
- Excel report: job_search_result_YYYYMMDD_HHMMSS.xlsx
  - Sheet: Job Search Results
  - Columns include: relevance score, score reasons, job title, company, location, salary, short description, application link, visa status, company Glassdoor link, application status, cover letter generated
- Cover letters (optional): job_search_results/<Month_Day_Year>/cover_letters/*.docx

## What it does

1. Reads CV text using pdfplumber
2. Extracts skills, experience, education, projects, certifications with regex heuristics
3. Builds search queries, calls SerpAPI google_jobs engine
4. Scores jobs using skill matches and visa/location indicators
5. Writes results to Excel, adds dropdown validation for application status if possible
6. Optionally generates cover letters using OpenAI, saves as .docx

## Scoring rules

- Skill match: +10 points per matching skill
- Explicit visa sponsorship mention: +100 points
- Sponsor-friendly location: +50 points
- Target country match: +75 points
- Remote work: +30 points

## Troubleshooting

- ModuleNotFoundError:
  - Activate the virtualenv, run pip install -r requirements.txt, run from project root so imports resolve.
- CV file not found:
  - Ensure CV_PATH is a full path to a readable PDF. Use forward slashes / on Unix, escape backslashes on Windows.
- pdfplumber returns empty text:
  - PDF might be image-based, use OCR first or provide a text-based PDF.
- SerpAPI errors or empty results:
  - Verify SERPAPI_KEY, confirm your SerpAPI plan supports the google_jobs engine, check network and rate limits.
- OpenAI errors or AttributeError: module 'openai' has no attribute 'OpenAI':
  - The code uses the newer OpenAI client pattern openai.OpenAI(api_key=...). If your installed openai package is older, either upgrade it, or modify letters/cover_letter_generator.py to use openai.api_key = os.getenv('OPENAI_API_KEY') and openai.ChatCompletion.create(...) or adapt to your SDK.
- Excel dropdown not added:
  - openpyxl must be installed and the writer must support validations. The code falls back to writing Excel without validation on error.

## Customization

- Convert interactive prompts to CLI flags using argparse for headless runs, or accept a JSON config file.
- Edit visa keywords in jobs/scoring.py VISA_KEYWORDS
- Edit sponsor-friendly countries in config/config.py
- Adjust query generation in jobs/queries.py to change search breadth or depth

## Notes for maintainers

- Run from project root so relative imports work
- Pin package versions in requirements.txt for reproducible installs
- If you want a Dockerfile or a scheduled job setup, specify the exact behavior and I will provide it.
