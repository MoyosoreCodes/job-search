import os
from typing import Optional

class Common:
    @staticmethod
    def getenv_or_prompt(key: str, prompt_text: str, optional: bool = False) -> Optional[str]:
        v = os.getenv(key, "").strip()
        if v:
            return v
        try:
            if optional:
                val = input(f"{prompt_text} (optional, leave blank to skip): ").strip()
                return val or None
            val = ""
            while not val:
                val = input(f"{prompt_text}: ").strip()
            return val
        except EOFError:
            return None if optional else ""

    @staticmethod
    def yes_no(prompt_text: str, default_yes: bool = True) -> bool:
        default = "Y/n" if default_yes else "y/N"
        try:
            ans = input(f"{prompt_text} [{default}]: ").strip().lower()
        except EOFError:
            ans = ""
        if not ans:
            return default_yes
        return ans in {"y", "yes"}

    @staticmethod
    def coalesce(*vals):
        for v in vals:
            if v:
                return v
        return ""
