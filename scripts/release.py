"""Release helper: bump version, commit, tag, and push.

Usage:
    python scripts/release.py 1.2.0
    python scripts/release.py v1.2.0   # leading 'v' is stripped automatically
"""

import re
import sys
import json
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to repo root, which is one level up from this script)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
CONSTANTS_FILE = ROOT / "job_search_app" / "constants.py"
VERSION_JSON   = ROOT / "version.json"

RELEASE_ASSET_URL = (
    "https://github.com/Moyo-x/job-search-api/releases/download"
    "/v{version}/AI Job Search.exe"
)

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True,
                          capture_output=True, cwd=ROOT)


def git_status_clean() -> bool:
    result = run(["git", "status", "--porcelain"], check=False)
    return result.stdout.strip() == ""


def current_version() -> str:
    text = CONSTANTS_FILE.read_text(encoding="utf-8")
    m = re.search(r'^VERSION\s*=\s*["\'](.+?)["\']', text, re.MULTILINE)
    if not m:
        raise RuntimeError("Could not find VERSION in constants.py")
    return m.group(1)


def set_version_in_constants(version: str) -> None:
    text = CONSTANTS_FILE.read_text(encoding="utf-8")
    new_text = re.sub(
        r'^(VERSION\s*=\s*)["\'].+?["\']',
        lambda m: f'{m.group(1)}"{version}"',
        text,
        flags=re.MULTILINE,
    )
    CONSTANTS_FILE.write_text(new_text, encoding="utf-8")


def update_version_json(version: str) -> None:
    data = {
        "version": version,
        "url": RELEASE_ASSET_URL.format(version=version),
    }
    VERSION_JSON.write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <version>  (e.g. 1.2.0)")
        sys.exit(1)

    version = sys.argv[1].lstrip("v")

    if not SEMVER_RE.match(version):
        print(f"Error: '{version}' is not a valid semver (expected X.Y.Z)")
        sys.exit(1)

    old_version = current_version()
    if version == old_version:
        print(f"Error: version is already {old_version}")
        sys.exit(1)

    # Warn about uncommitted changes (not fatal — release files will be committed)
    if not git_status_clean():
        print("Warning: working tree has uncommitted changes.")
        answer = input("Continue anyway? [y/N] ").strip().lower()
        if answer != "y":
            sys.exit(0)

    print(f"Bumping {old_version} -> {version}")

    # 1. Update source files
    set_version_in_constants(version)
    update_version_json(version)
    print("  Updated constants.py and version.json")

    # 2. Stage
    run(["git", "add",
         str(CONSTANTS_FILE.relative_to(ROOT)),
         str(VERSION_JSON.relative_to(ROOT))])

    # 3. Commit
    run(["git", "commit", "-m", f"release: bump to v{version}"])
    print(f"  Committed: release: bump to v{version}")

    # 4. Tag
    run(["git", "tag", f"v{version}"])
    print(f"  Tagged: v{version}")

    # 5. Push branch + tags
    run(["git", "push"])
    run(["git", "push", "--tags"])
    print("  Pushed branch and tags")

    print(f"\nDone! GitHub Actions will now build and publish v{version}.")
    print(f"Watch the release at: https://github.com/Moyo-x/job-search-api/releases")


if __name__ == "__main__":
    main()
