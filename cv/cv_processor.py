from pathlib import Path
from typing import Dict, List, Tuple
import re

class CVProcessor:
    def extract_text(self, pdf_path: str) -> str:
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for p in pdf.pages:
                    text += (p.extract_text() or "") + "\n"
        except Exception:
            text = ""
        return text.strip()

    def extract_sections(self, text: str) -> Dict[str, str]:
        headers = ["skills", "experience", "education", "projects", "certifications", "summary", "profile"]
        pattern = r"(?im)^\s*(" + "|".join([re.escape(h) for h in headers]) + r")\s*[:\-]?\s*$"
        chunks: List[Tuple[str, int, int]] = []
        for m in re.finditer(pattern, text):
            chunks.append((m.group(1).lower(), m.start(), m.end()))
        sections: Dict[str, str] = {}
        if not chunks:
            sections["all"] = text
            return sections
        for i, (name, _, endpos) in enumerate(chunks):
            start = endpos
            stop = chunks[i + 1][1] if i + 1 < len(chunks) else len(text)
            sections[name] = text[start:stop].strip()
        return sections

    def extract_skills(self, cv_path: str) -> List[str]:
        text = self.extract_text(cv_path)
        sections = self.extract_sections(text)
        pool = sections.get("skills") or sections.get("summary") or sections.get("profile") or sections.get("all", "")
        tokens = re.split(r"[\n,;|/]", pool)
        skills = []
        for t in tokens:
            v = re.sub(r"[^A-Za-z0-9\+\.#\- ]", "", t).strip()
            if v and len(v) <= 64:
                skills.append(v)
        dedup = []
        seen = set()
        for s in skills:
            k = s.lower()
            if k not in seen:
                seen.add(k)
                dedup.append(s)
        return dedup[:128]
