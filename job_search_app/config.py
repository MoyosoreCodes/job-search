"""Config file load / save helpers."""
import json
import os

CONFIG_FILE = "config.json"


def load_config(filepath: str = CONFIG_FILE) -> dict:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        print(f"Could not load config: {exc}")
        return {}


def save_config(data: dict, filepath: str = CONFIG_FILE) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except Exception as exc:
        print(f"Could not save config: {exc}")
