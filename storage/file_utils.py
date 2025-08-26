import re
import unicodedata
from pathlib import Path
from typing import Union
from docx import Document

class FileUtils:
    @staticmethod
    def ensure_dir(p: Union[str, Path]) -> Path:
        path = Path(p)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def sanitize_filename(s: str, max_len: int = 80) -> str:
        s = str(s or "")
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        s = s.strip()
        s = re.sub(r'[\\/:"*?<>|]+', "", s)
        s = re.sub(r"\s+", "_", s)
        if len(s) > max_len:
            s = s[:max_len].rstrip("_")
        return s or "untitled"

    @staticmethod
    def save_docx(lines: str, path: Union[str, Path]) -> str:
        d = Document()
        for line in str(lines or "").splitlines():
            d.add_paragraph(line)
        d.save(path)
        return str(path)
