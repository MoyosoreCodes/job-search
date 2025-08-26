from typing import Dict, Optional
from pathlib import Path
from config.config import AppConfig
from storage.file_utils import FileUtils

class CoverLetterGenerator:
    def __init__(self, openai_key: str):
        self.openai_key = openai_key

    def generate_text(self, job: Dict, cv_snippet: Optional[str] = None) -> str:
        if self.openai_key:
            t = self._generate_openai(job, cv_snippet)
            if t:
                return t
        return self._fallback_text(job, cv_snippet)

    def _generate_openai(self, job: Dict, cv_snippet: Optional[str]) -> Optional[str]:
        try:
            import openai
        except Exception:
            return None
        prompt = []
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")
        if title:
            prompt.append(f"Write a professional one-page cover letter for the role: {title}.")
        if company:
            prompt.append(f"Company: {company}.")
        if location:
            prompt.append(f"Location: {location}.")
        if cv_snippet:
            prompt.append("Incorporate these candidate highlights:")
            prompt.append(cv_snippet)
        content = "\n".join(prompt).strip()
        try:
            if hasattr(openai, "OpenAI"):
                client = openai.OpenAI(api_key=self.openai_key)
                resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":content}], max_tokens=700)
                return resp.choices[0].message.content.strip()
            openai.api_key = self.openai_key
            resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":content}], max_tokens=700)
            return resp.choices[0].message["content"].strip()
        except Exception:
            return None

    def _fallback_text(self, job: Dict, cv_snippet: Optional[str]) -> str:
        title = job.get("title", "the advertised position")
        company = job.get("company", "")
        lines = []
        lines.append(f"Dear Hiring Team at {company}," if company else "Dear Hiring Team,")
        lines.append("")
        lines.append(f"I am writing to express my interest in the {title} role.")
        if cv_snippet:
            lines.append("")
            lines.append("Key highlights from my background:")
            lines.append(cv_snippet)
        lines.append("")
        lines.append("I believe my experience and skills align with the requirements and I would welcome the opportunity to discuss further.")
        lines.append("")
        lines.append("Sincerely,")
        lines.append("")
        lines.append("Your Name")
        return "\n".join(lines)

    def generate_and_save(self, job: Dict, row_number: int, output_dir: Path) -> str:
        text = self.generate_text(job, job.get("cv_snippet"))
        FileUtils.ensure_dir(output_dir)
        safe_title = FileUtils.sanitize_filename(job.get("title", "untitled"))
        filename = f"{row_number:04d}_{safe_title}.docx"
        path = output_dir / filename
        return FileUtils.save_docx(text, path)
