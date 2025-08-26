import re

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\s-]', '', name).strip()
