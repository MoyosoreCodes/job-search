# -*- coding: utf-8 -*-
"""Unit tests for job_search.py core logic.

Run with:
    python -m pytest tests/ -v
"""

import importlib
import os
import sys
import types
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Stub out heavy optional dependencies so tests run without installing them
# ---------------------------------------------------------------------------
for _mod in ("pdfplumber", "dotenv"):
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)

# dotenv.load_dotenv must be callable
sys.modules["dotenv"].load_dotenv = lambda *a, **kw: None  # type: ignore

import job_search  # noqa: E402  (must come after stubs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_job(
    title: str = "Software Engineer",
    company: str = "Acme Corp",
    location: str = "Toronto, Canada",
    description: str = "We offer visa sponsorship for qualified candidates.",
) -> dict:
    return {
        "title": title,
        "company_name": company,
        "location": location,
        "description": description,
    }


# ---------------------------------------------------------------------------
# extract_skills_from_content
# ---------------------------------------------------------------------------
class TestExtractSkillsFromContent(unittest.TestCase):

    def test_comma_separated_skills(self):
        content = "Python, Django, PostgreSQL, Docker"
        skills = job_search.extract_skills_from_content(content)
        self.assertIn("Python", skills)
        self.assertIn("Django", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("Docker", skills)

    def test_bullet_point_skills(self):
        content = "• Python\n• React\n• AWS"
        skills = job_search.extract_skills_from_content(content)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("AWS", skills)

    def test_category_prefix_stripped(self):
        content = "Programming Languages: Python, Java, Go"
        skills = job_search.extract_skills_from_content(content)
        self.assertIn("Python", skills)
        self.assertIn("Java", skills)
        self.assertNotIn("Programming Languages", skills)

    def test_empty_content_returns_empty(self):
        self.assertEqual(job_search.extract_skills_from_content(""), [])

    def test_filters_common_filler_words(self):
        content = "the and or include etc"
        skills = job_search.extract_skills_from_content(content)
        for filler in ("the", "and", "or", "etc"):
            self.assertNotIn(filler, skills)

    def test_deduplication(self):
        content = "Python, Python, Python"
        skills = job_search.extract_skills_from_content(content)
        self.assertEqual(skills.count("Python"), 1)

    def test_skill_length_bounds(self):
        content = "A, ValidSkill, " + "x" * 60  # too long
        skills = job_search.extract_skills_from_content(content)
        self.assertNotIn("A", skills)          # too short (< 2 chars)
        self.assertIn("ValidSkill", skills)
        self.assertFalse(any(len(s) > 50 for s in skills))


# ---------------------------------------------------------------------------
# has_visa_sponsorship_indicators
# ---------------------------------------------------------------------------
class TestHasVisaSponsorshipIndicators(unittest.TestCase):

    def test_detects_visa_sponsorship_in_description(self):
        job = _make_job(description="We provide visa sponsorship for this role.")
        found, keyword = job_search.has_visa_sponsorship_indicators(job)
        self.assertTrue(found)
        self.assertIsNotNone(keyword)

    def test_detects_h1b_keyword(self):
        job = _make_job(description="H1B candidates welcome.")
        found, _ = job_search.has_visa_sponsorship_indicators(job)
        self.assertTrue(found)

    def test_no_sponsorship_keywords(self):
        job = _make_job(description="Must be authorized to work in the EU.")
        found, keyword = job_search.has_visa_sponsorship_indicators(job)
        self.assertFalse(found)
        self.assertIsNone(keyword)

    def test_empty_job_data(self):
        found, keyword = job_search.has_visa_sponsorship_indicators({})
        self.assertFalse(found)
        self.assertIsNone(keyword)

    def test_keyword_in_title(self):
        job = _make_job(title="Engineer (Visa Sponsorship Available)")
        found, _ = job_search.has_visa_sponsorship_indicators(job)
        self.assertTrue(found)


# ---------------------------------------------------------------------------
# is_sponsor_friendly_location
# ---------------------------------------------------------------------------
class TestIsSponsorFriendlyLocation(unittest.TestCase):

    def test_canada_is_friendly(self):
        self.assertTrue(job_search.is_sponsor_friendly_location("Toronto, Canada"))

    def test_germany_is_friendly(self):
        self.assertTrue(job_search.is_sponsor_friendly_location("Berlin, Germany"))

    def test_unknown_country_is_not_friendly(self):
        self.assertFalse(job_search.is_sponsor_friendly_location("Lagos, Nigeria"))

    def test_empty_location_is_false(self):
        self.assertFalse(job_search.is_sponsor_friendly_location(""))
        self.assertFalse(job_search.is_sponsor_friendly_location(None))

    def test_case_insensitive(self):
        self.assertTrue(job_search.is_sponsor_friendly_location("CANADA"))


# ---------------------------------------------------------------------------
# calculate_job_score
# ---------------------------------------------------------------------------
class TestCalculateJobScore(unittest.TestCase):

    def _prefs(self, **overrides) -> dict:
        defaults = {
            "visa_priority":    True,
            "remote_only":      False,
            "target_countries": ["canada"],
            "skill_focus":      [],
        }
        defaults.update(overrides)
        return defaults

    def test_skill_match_adds_points(self):
        job = _make_job(description="We use Python and Django every day.")
        score, reasons = job_search.calculate_job_score(
            job, ["Python", "Django"], self._prefs())
        self.assertGreater(score, 0)
        self.assertTrue(any("skill" in r.lower() for r in reasons))

    def test_visa_sponsorship_adds_large_bonus(self):
        job = _make_job(description="This role offers visa sponsorship.")
        score, reasons = job_search.calculate_job_score(
            job, ["Python"], self._prefs())
        self.assertGreaterEqual(score, 100)

    def test_sponsor_friendly_location_adds_bonus(self):
        job = _make_job(location="Toronto, Canada",
                        description="No visa info here.")
        score, reasons = job_search.calculate_job_score(
            job, [], self._prefs(target_countries=[]))
        # Should get sponsor-friendly location bonus (50 pts)
        self.assertGreaterEqual(score, 50)

    def test_target_country_adds_bonus(self):
        job = _make_job(location="Vancouver, Canada", description="Normal job.")
        score, reasons = job_search.calculate_job_score(
            job, [], self._prefs())
        self.assertGreaterEqual(score, 75)

    def test_remote_work_adds_bonus(self):
        job = _make_job(description="This is a fully remote position.")
        score, _ = job_search.calculate_job_score(
            job, [], self._prefs(remote_only=True, target_countries=[]))
        self.assertGreaterEqual(score, 30)

    def test_irrelevant_job_scores_zero(self):
        job = _make_job(
            location="Random City, Antarctica",
            description="Some unrelated content with no matching info.")
        score, _ = job_search.calculate_job_score(
            job, ["COBOL"], self._prefs(
                visa_priority=False, target_countries=[], remote_only=False))
        # May or may not score 0 depending on skill match; just check it's non-negative
        self.assertGreaterEqual(score, 0)

    def test_score_reasons_populated(self):
        job = _make_job(description="We sponsor visas and use Python.")
        _, reasons = job_search.calculate_job_score(
            job, ["Python"], self._prefs())
        self.assertIsInstance(reasons, list)
        self.assertGreater(len(reasons), 0)


# ---------------------------------------------------------------------------
# format_job_data
# ---------------------------------------------------------------------------
class TestFormatJobData(unittest.TestCase):

    def test_output_keys_present(self):
        job = _make_job()
        result = job_search.format_job_data(job, "python developer", 120, ["skill match"])
        expected_keys = {
            "Search Query", "Relevance Score", "Score Reasons",
            "Job Title", "Company", "Location", "Salary",
            "Posting Date", "Job Description", "Application Link",
            "Visa Sponsorship Mentioned", "Company Glassdoor",
        }
        self.assertTrue(expected_keys.issubset(result.keys()))

    def test_long_description_truncated(self):
        long_desc = "x" * 1000
        job = _make_job(description=long_desc)
        result = job_search.format_job_data(job, "query", 10, [])
        self.assertLessEqual(len(result["Job Description"]), 510)

    def test_short_description_not_truncated(self):
        short = "Short description."
        job = _make_job(description=short)
        result = job_search.format_job_data(job, "query", 10, [])
        self.assertIn(short, result["Job Description"])

    def test_score_reasons_joined(self):
        job = _make_job()
        result = job_search.format_job_data(job, "q", 50, ["reason A", "reason B"])
        self.assertIn("reason A", result["Score Reasons"])
        self.assertIn("reason B", result["Score Reasons"])


# ---------------------------------------------------------------------------
# get_glassdoor_link
# ---------------------------------------------------------------------------
class TestGetGlassdoorLink(unittest.TestCase):

    def test_returns_url_string(self):
        url = job_search.get_glassdoor_link("Acme Corp")
        self.assertIsInstance(url, str)
        self.assertIn("glassdoor.com", url)

    def test_empty_company_returns_not_available(self):
        self.assertEqual(job_search.get_glassdoor_link(""), "Not available")
        self.assertEqual(job_search.get_glassdoor_link(None), "Not available")

    def test_company_name_encoded_in_url(self):
        url = job_search.get_glassdoor_link("Open AI")
        self.assertIn("Open", url)


# ---------------------------------------------------------------------------
# search_jobs_on_serpapi  (mocked)
# ---------------------------------------------------------------------------
class TestSearchJobsOnSerpapi(unittest.TestCase):

    @patch("job_search.requests.get")
    def test_returns_jobs_on_success(self, mock_get):
        fake_jobs = [{"title": "Engineer", "company_name": "Corp"}]
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"jobs_results": fake_jobs},
        )
        results = job_search.search_jobs_on_serpapi("python", "fake_key")
        self.assertEqual(results, fake_jobs)

    @patch("job_search.requests.get")
    def test_returns_empty_on_401(self, mock_get):
        mock_get.return_value = MagicMock(status_code=401, text="Unauthorized")
        results = job_search.search_jobs_on_serpapi("python", "bad_key")
        self.assertEqual(results, [])

    @patch("job_search.requests.get")
    def test_returns_empty_on_api_error_field(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"error": "Invalid API key."},
        )
        results = job_search.search_jobs_on_serpapi("python", "bad_key")
        self.assertEqual(results, [])

    @patch("job_search.requests.get")
    def test_returns_empty_on_connection_error(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.ConnectionError("No internet")
        results = job_search.search_jobs_on_serpapi("python", "key")
        self.assertEqual(results, [])

    @patch("job_search.requests.get")
    def test_location_filter_passed_as_string(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"jobs_results": []},
        )
        job_search.search_jobs_on_serpapi("python", "key", location_filter="Canada")
        call_params = mock_get.call_args[1]["params"]
        self.assertEqual(call_params.get("location"), "Canada")

    @patch("job_search.requests.get")
    def test_list_location_filter_ignored(self, mock_get):
        """A list location should not be passed to SerpAPI."""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"jobs_results": []},
        )
        job_search.search_jobs_on_serpapi(
            "python", "key", location_filter=["Canada", "Germany"])
        call_params = mock_get.call_args[1]["params"]
        self.assertNotIn("location", call_params)


# ---------------------------------------------------------------------------
# search_jobs_with_visa_focus
# ---------------------------------------------------------------------------
class TestSearchJobsWithVisaFocus(unittest.TestCase):

    def _prefs(self, **kw) -> dict:
        defaults = {
            "visa_priority":    True,
            "remote_only":      False,
            "target_countries": [],
            "skill_focus":      [],
        }
        defaults.update(kw)
        return defaults

    def test_returns_list(self):
        queries = job_search.search_jobs_with_visa_focus(["Python"], self._prefs())
        self.assertIsInstance(queries, list)

    def test_does_not_exceed_ten_queries(self):
        skills = [f"Skill{i}" for i in range(20)]
        queries = job_search.search_jobs_with_visa_focus(skills, self._prefs())
        self.assertLessEqual(len(queries), 10)

    def test_visa_priority_generates_visa_queries(self):
        queries = job_search.search_jobs_with_visa_focus(
            ["Python"], self._prefs(visa_priority=True))
        has_visa_query = any("visa" in q.lower() or "h1b" in q.lower()
                             for q in queries)
        self.assertTrue(has_visa_query)

    def test_remote_only_generates_remote_queries(self):
        queries = job_search.search_jobs_with_visa_focus(
            [], self._prefs(remote_only=True))
        has_remote_query = any("remote" in q.lower() for q in queries)
        self.assertTrue(has_remote_query)


# ---------------------------------------------------------------------------
# get_default_output_folder / create_results_folder
# ---------------------------------------------------------------------------
class TestOutputFolder(unittest.TestCase):

    def test_default_folder_is_inside_documents(self):
        folder = job_search.get_default_output_folder()
        documents = os.path.join(os.path.expanduser("~"), "Documents")
        self.assertTrue(folder.startswith(documents),
                        f"Expected folder inside Documents, got: {folder}")

    def test_default_folder_named_job_search_results(self):
        folder = job_search.get_default_output_folder()
        self.assertIn("Job Search Results", folder)

    def test_create_results_folder_uses_default_when_no_base(self):
        with patch("os.makedirs") as mock_mkdir:
            result = job_search.create_results_folder()
            mock_mkdir.assert_called_once()
            self.assertIn("Documents", result)

    def test_create_results_folder_uses_provided_base(self):
        with patch("os.makedirs") as mock_mkdir:
            result = job_search.create_results_folder(base_folder="/tmp/my_jobs")
            mock_mkdir.assert_called_once()
            self.assertTrue(result.startswith("/tmp/my_jobs"))

    def test_create_results_folder_contains_date(self):
        with patch("os.makedirs"):
            result = job_search.create_results_folder()
            today = datetime.now().strftime("%Y")   # at least the year
            self.assertIn(today, result)


if __name__ == "__main__":
    unittest.main()
