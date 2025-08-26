import re
import os
from typing import List, Dict
import pdfplumber

class CVProcessor:
    def __init__(self, cv_path: str):
        self.cv_path = cv_path
        self.default_sections = {
            'skills': 'Skills',
            'experience': 'Experience',
            'education': 'Education',
            'certifications': 'Certifications',
            'projects': 'Projects'
        }

    def extract_text(self) -> str:
        if not os.path.exists(self.cv_path):
            print(f"CV file not found: {self.cv_path}")
            return None
        try:
            with pdfplumber.open(self.cv_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def get_section_headers(self) -> Dict[str, str]:
        print("\n=== RESUME SECTION IDENTIFICATION ===")
        print("Specify section headers (press Enter for defaults):")
        sections = {}
        for key, default in self.default_sections.items():
            user_input = input(f"{key.title()} section (default: '{default}'): ").strip()
            sections[key] = user_input if user_input else default
        return sections

    def extract_section_content(self, cv_text: str, section_name: str) -> str:
        if not cv_text or not section_name:
            return ""
        pattern = rf'(?i){re.escape(section_name)}\s*:?\s*[\r\n]+(.*?)(?=\n[A-Z][a-zA-Z\s&]*\s*:?\s*[\r\n]|\n\s*\n|\Z)'
        match = re.search(pattern, cv_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def extract_skills(self, content: str) -> List[str]:
        skills = set()
        for line in content.split('\n'):
            line = line.strip()
            if not line or len(line) < 3:
                continue
            line = re.sub(r'^[•\-\*]\s*', '', line)
            line = re.sub(r'^(Programming Languages?|Technologies?|Frameworks?)\s*[:\-]?\s*', '', line, flags=re.IGNORECASE)
            for item in re.split(r'[,;]+', line):
                item = item.strip('.,;:•\-() ').strip()
                if (item and 2 <= len(item) <= 50 and not re.match(r'^(the|and|or|with|using)$', item, re.IGNORECASE)):
                    skills.add(item)
        return list(skills)

    def validate_content(self, content_type: str, content, is_list: bool = False):
        if is_list and not content:
            print(f"No {content_type} extracted")
            return []
        if not is_list and not content:
            print(f"No {content_type} content extracted")
            return ""
        print(f"\n=== EXTRACTED {content_type.upper()} ===")
        if is_list:
            print(f"Found {len(content)} {content_type}:")
            for i, item in enumerate(content, 1):
                print(f"  {i:2d}. {item}")
        else:
            preview = content[:300] + "..." if len(content) > 300 else content
            print(f"Content preview: {preview}")
        confirm = input(f"Does this {content_type} look correct? (y/n, default: y): ").strip().lower()
        if confirm in ['n', 'no']:
            if is_list:
                add_items = input(f"Add {content_type} (comma-separated): ").strip()
                remove_items = input(f"Remove {content_type} (comma-separated): ").strip()
                if add_items:
                    content.extend([s.strip() for s in add_items.split(',') if s.strip()])
                if remove_items:
                    remove_list = [s.strip().lower() for s in remove_items.split(',')]
                    content = [s for s in content if s.lower() not in remove_list]
                return list(dict.fromkeys(content))
            else:
                print(f"Please update your CV's {content_type} section and restart.")
                return ""
        return list(dict.fromkeys(content)) if is_list else content

    def extract_all_sections(self, cv_text: str, section_headers: Dict[str, str]) -> Dict:
        resume_data = {
            "skills": [], "experience": [], "education": [],
            "projects": [], "certifications": [], "contact_info": {}
        }

        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', cv_text)
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', cv_text)
        if emails:
            resume_data["contact_info"]["email"] = emails[0]
        if phones:
            resume_data["contact_info"]["phone"] = phones[0]

        skills_content = self.extract_section_content(cv_text, section_headers.get('skills', self.default_sections['skills']))
        if skills_content:
            resume_data["skills"] = self.extract_skills(skills_content)
            resume_data["skills"] = self.validate_content("skills", resume_data["skills"], is_list=True)

        for section in ['experience', 'education', 'projects', 'certifications']:
            content = self.extract_section_content(cv_text, section_headers.get(section, self.default_sections[section]))
            if not content:
                continue
            if section == 'experience':
                jobs = re.split(r'\n(?=[A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager))', content)
                resume_data[section] = [job.strip()[:500] for job in jobs[:3] if len(job.strip()) > 50]
            elif section == 'education':
                degrees = re.findall(r'(Bachelor|Master|PhD|B\.S\.|M\.S\.).*?\n', content, re.IGNORECASE)
                resume_data[section] = [deg.strip() for deg in degrees]
            else:
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                cleaned_lines = []
                for line in lines[:5]:
                    line = re.sub(r'^[•\-\*]\s*', '', line)
                    if len(line) > 10:
                        cleaned_lines.append(line[:300] if section == 'projects' else line)
                resume_data[section] = cleaned_lines

        return resume_data
