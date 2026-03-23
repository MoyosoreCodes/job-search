# AI-Powered Job Search with Visa Sponsorship Priority

An intelligent job search desktop application that extracts skills from your CV and finds visa-sponsored roles tailored to your background.

---

## Features

- **CV-Driven Skill Extraction** — Automatically reads skills from your resume (PDF or DOCX)
- **Visa Sponsorship Priority** — Scores and highlights jobs that explicitly mention visa sponsorship
- **Smart Scoring System** — Ranks jobs by skill relevance, location, and visa friendliness
- **Interactive Result Previewer** — Browse every job in a split-panel view with full details and one-click Apply
- **Load Saved Results** — Re-open any previously exported Excel or CSV file in the previewer
- **Filter & Sort** — Live filter by keyword, visa status, score, date, or company name
- **Export Reports** — Save results as Excel (.xlsx) or CSV to a folder of your choice
- **Auto-Save Config** — API key, CV path, and preferences are remembered between sessions
- **Standalone EXE** — No Python installation required; just run `AI Job Search.exe`

---

## Download

Pre-built Windows executable:

```
dist/AI Job Search.exe
```

Double-click to launch. No installation needed.

---

## Wizard Tabs

| Tab | Purpose |
|-----|---------|
| **Configuration** | SerpAPI key, CV file path, output folder and format |
| **Preferences** | Job title, skills section name, target countries, visa/remote toggles |
| **CV Preview** | Extracted text from your CV (refresh at any time) |
| **Skills** | Editable list of skills extracted from your CV |
| **Results** | Search log, interactive job list and detail previewer |

---

## Results Previewer

After a search completes (or after loading a saved file), the **Results** tab switches to a split-panel view:

```
+-------------------+------------------------------------------+
|  Filter / Sort    |                                          |
+-------------------+  [Apply Now]  [Glassdoor]  [Copy Link]  |
|  Job Title    Sc  |                                          |
|  ------------ --  |  Senior Python Developer                 |
|  Sr. Python   185 |  Google  *  New York, USA               |
|  Backend Eng  160 |  ----------------------------------------|
|  Full Stack   140 |  Posted:   3 days ago                    |
|  ...              |  Salary:   $120k - $180k                 |
|                   |  Visa:     Sponsorship confirmed          |
|                   |  Score:    185                            |
|                   |  Reasons:  5 skill matches; visa keyword  |
|                   |  ----------------------------------------|
|                   |  DESCRIPTION                             |
|                   |  We are looking for a senior Python...   |
+-------------------+------------------------------------------+
```

### Row colours
| Colour | Meaning |
|--------|---------|
| Green  | Visa sponsorship explicitly mentioned |
| Yellow | Sponsor-friendly country/location |
| White  | No visa signals detected |

### Action buttons
- **Apply Now** — Opens the application link in your browser
- **Glassdoor** — Opens Glassdoor reviews for the company
- **Copy Link** — Copies the application URL to the clipboard

### Filter bar
- Type any keyword to filter by title, company, location, or score reasons
- Filter by visa status: All / Yes / Maybe / Unknown
- Sort by: Score (high→low / low→high), Date, Company A–Z

### Loading a saved file
Click **Load File** (top-left of the Results tab) and choose any `.xlsx` or `.csv` exported by this tool. All details and links are preserved.

---

## Scoring System

| Signal | Points |
|--------|--------|
| Per matching skill found in job text | +10 |
| Explicit visa sponsorship keyword | +100 |
| Sponsor-friendly country (US, CA, DE, etc.) | +50 |
| Job in a target country you selected | +75 |
| Remote work available (when toggled on) | +30 |
| Per additional skill-focus match | +25 |

---

## Output Columns (Excel / CSV)

| Column | Description |
|--------|-------------|
| Relevance Score | Numeric score (higher = better match) |
| Score Reasons | Why the job scored well |
| Job Title | Position title |
| Company | Company name |
| Location | Job location |
| Salary | Salary range (if available) |
| Posting Date | When the job was posted |
| Job Description | First 500 characters of the description |
| Application Link | Direct application URL |
| Visa Sponsorship Mentioned | Yes / Maybe / Unknown |
| Company Glassdoor | Glassdoor review search link |
| Search Query | Which search query found this job |

---

## Running from Source

### Prerequisites
- Python 3.9+
- SerpAPI account — [serpapi.com](https://serpapi.com/) (free tier: 100 searches/month)

### Install dependencies
```bash
pip install -r requirements.txt
```

### Launch the GUI
```bash
python job_search_gui.py
```

### Run tests
```bash
pytest tests/ -v
```

---

## Building the EXE

```bash
python -m PyInstaller job_search_gui.spec --noconfirm
```

Output: `dist/AI Job Search.exe`

---

## Sponsor-Friendly Countries (built-in)

United States, Canada, Germany, Netherlands, Ireland, Australia, New Zealand, United Kingdom, Sweden, Denmark, Switzerland, Austria, Singapore

---

## Troubleshooting

**"CV file not found"**
- Check that the full path in the Configuration tab is correct
- Use the Browse button to select the file directly

**"No skills found"**
- Confirm the Skills Section Name in Preferences matches your CV exactly (e.g. `Skills`, `Technical Skills`)
- Click the Refresh button on the CV Preview tab to confirm text was extracted

**Search returns no results**
- Verify the SerpAPI key is valid (check the [SerpAPI dashboard](https://serpapi.com/manage-api-key))
- Try selecting a single target country in Preferences
- Reduce the number of selected countries to avoid rate limits

**SerpAPI 429 error**
- You have reached your monthly search quota; wait for the quota to reset or upgrade your plan

**Excel file won't open**
- Ensure `openpyxl` is installed: `pip install openpyxl`
- Try saving as CSV instead (Configuration → Output Format)
