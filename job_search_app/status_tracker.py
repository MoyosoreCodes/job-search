"""Persist job application statuses across sessions."""
import json
import os

STATUS_FILE = os.path.expanduser("~/.job_search_statuses.json")

STATUSES = ("Applied", "Interested", "Rejected")

STATUS_LABELS: dict[str, str] = {
    "Applied":    "🟢 Applied",
    "Interested": "⭐ Interested",
    "Rejected":   "❌ Rejected",
    "":           "⬜ Clear",
}


class StatusTracker:
    """Thread-safe in-memory status store backed by a JSON file."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self.load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def load(self) -> None:
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r", encoding="utf-8") as fh:
                    self._data = json.load(fh)
        except Exception:
            self._data = {}

    def save(self) -> None:
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2)
        except Exception as exc:
            print(f"Could not save statuses: {exc}")

    # ── Key helper ────────────────────────────────────────────────────────────

    @staticmethod
    def key(job: dict) -> str:
        """Stable identifier: 'Job Title||Company'."""
        return f"{job.get('Job Title', '')}||{job.get('Company', '')}"

    # ── Read / write ──────────────────────────────────────────────────────────

    def get(self, job: dict) -> str:
        return self._data.get(self.key(job), "")

    def set(self, job: dict, status: str) -> None:
        k = self.key(job)
        if status:
            self._data[k] = status
        else:
            self._data.pop(k, None)
        self.save()
