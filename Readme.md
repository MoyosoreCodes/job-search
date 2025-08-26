# 🚀 AI-Powered Job Search with Visa Sponsorship Priority

An intelligent job search automation system that extracts skills from your CV and finds visa sponsorship opportunities tailored to your background.

## 🌟 Features

- **🎯 CV-Driven Skill Extraction**: Automatically extracts skills from your resume's skills section
- **🌍 Visa Sponsorship Priority**: Prioritizes jobs that explicitly mention visa sponsorship
- **🔍 Smart Job Matching**: Scores jobs based on skill relevance and visa potential  
- **📊 Comprehensive Reports**: Generates detailed Excel reports with job details and application links
- **🛠️ User-Friendly Setup**: Interactive prompts for easy configuration
- **🌐 Global Coverage**: Searches across sponsor-friendly countries (US, Canada, Germany, etc.)

## 📋 Prerequisites

- Python 3.7+
- SerpAPI account (free tier available)
- CV in PDF format

## 🚀 Installation

1. **Clone or download the script**
   ```bash
   git clone <repository-url>
   cd job-search-system
   ```

2. **Install required packages**
   ```bash
   pip install requests pandas pdfplumber openpyxl
   ```

3. **Get your SerpAPI key**
   - Visit [SerpAPI.com](https://serpapi.com/)
   - Sign up for a free account
   - Navigate to your dashboard to get your API key
   - Free tier includes 100 searches/month

## 📖 Usage

### Step 1: Run the Script
```bash
python job_search.py
```

### Step 2: Interactive Setup
The system will guide you through:

1. **API Configuration**
   ```
   Enter your SerpAPI key: your_api_key_here
   ```

2. **CV File Path**
   ```
   Enter the path to your CV PDF file: /path/to/your/cv.pdf
   ```

3. **Skills Section Identification**
   ```
   Enter the name of your skills section (default: 'Skills'): Skills
   ```

4. **Skill Validation**
   - Review extracted skills
   - Add/remove skills if needed
   - Confirm final skills list

5. **Search Preferences**
   Choose your priority:
   - Visa sponsorship opportunities (default)
   - Specific countries/regions
   - Remote work opportunities
   - Focus on specific skills

### Step 3: Results
The system will:
- Search for relevant jobs using your skills
- Score jobs based on your preferences
- Generate a comprehensive Excel report
- Display top matches in the terminal

## 📊 Output Format

The generated Excel file includes:

| Column | Description |
|--------|-------------|
| **Relevance Score** | Job relevance score (higher = better match) |
| **Score Reasons** | Why the job scored well (skill matches, visa mentions) |
| **Job Title** | Position title |
| **Company** | Company name |
| **Location** | Job location |
| **Salary** | Salary range (if available) |
| **Posting Date** | When the job was posted |
| **Job Description** | Brief job description |
| **Application Link** | Direct application URL |
| **Visa Sponsorship Mentioned** | Yes/Maybe/Unknown |
| **Company Glassdoor** | Glassdoor company review link |

## 🎯 How It Works

### 1. Skills Extraction
```
Skills
• Programming Languages: JavaScript, Java, Go, C#, Node.js
• Database: PostgreSQL, MongoDB, MySQL
• DevOps & Tools: Docker, AWS, Git
```
↓ Extracts to: `JavaScript, Java, Go, C#, Node.js, PostgreSQL, MongoDB, MySQL, Docker, AWS, Git`

### 2. Intelligent Search Queries
- Basic skill searches: `"JavaScript"`, `"PostgreSQL"`
- Visa-focused searches: `"JavaScript visa sponsorship"`, `"Java h1b sponsor"`
- Location-specific: `"software developer Canada"`

### 3. Smart Scoring System
- **Skill Matches**: +10 points per matching skill
- **Explicit Visa Sponsorship**: +100 points
- **Sponsor-Friendly Location**: +50 points
- **Target Country**: +75 points
- **Remote Work**: +30 points

## 🔧 Customization

### Modify Search Preferences
Edit the preferences section in the script:
```python
preferences = {
    "visa_priority": True,
    "target_countries": ["canada", "germany"],
    "remote_only": False,
    "skill_focus": ["python", "react"]
}
```

### Add Custom Visa Keywords
Update the `VISA_KEYWORDS` list:
```python
VISA_KEYWORDS = [
    "visa sponsorship", "h1b", "work visa",
    "your custom keywords here"
]
```

### Extend Sponsor-Friendly Countries
Add to `SPONSOR_FRIENDLY_LOCATIONS`:
```python
SPONSOR_FRIENDLY_LOCATIONS = [
    "united states", "canada", "germany",
    "your target countries here"
]
```

## 🔍 Example CV Skills Section

The system works best with clearly structured skills sections:

```
Skills
• Programming Languages: JavaScript, Python, Java, TypeScript
• Frontend: React, Vue.js, HTML5, CSS3, Bootstrap
• Backend: Node.js, Express.js, Django, Flask
• Databases: PostgreSQL, MongoDB, Redis, MySQL
• Cloud & DevOps: AWS, Docker, Kubernetes, Git, Jenkins
• Tools: VS Code, Postman, Jira, Slack
```

## 🚨 Troubleshooting

### Common Issues

**❌ "CV file not found"**
- Ensure the file path is correct
- Use forward slashes (/) or escape backslashes (