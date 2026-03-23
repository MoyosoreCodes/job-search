"""AI-Powered Job Search — main application window."""
import os
import sys
import json
import threading
import tempfile
import subprocess
import webbrowser

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import docx
import requests

import job_search
from job_search_app.constants import C_BG, C_HEADER, C_WHITE, VERSION, VERSION_URL
from job_search_app.styles import apply_styles
from job_search_app.config import load_config as _load_cfg, save_config as _save_cfg
from job_search_app.tabs import config_tab, prefs_tab, cv_tab, skills_tab, results_tab

CONFIG_FILE = "config.json"


def _extract_text_from_docx(path: str) -> str | None:
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:
        print(f"Error reading DOCX: {exc}")
        return None


class JobSearchGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AI-Powered Job Search")
        self.geometry("1060x720")
        self.minsize(900, 600)
        self.configure(bg=C_BG)

        apply_styles(self)
        self._build_header()

        # Main content card
        main_frame = ttk.Frame(self, style="Card.TFrame", padding=12)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Notebook + tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        _tab_defs = [
            ("  ⚙  Configuration  ", config_tab),
            ("  ☑  Preferences  ",   prefs_tab),
            ("  📄  CV Preview  ",   cv_tab),
            ("  🛠  Skills  ",       skills_tab),
            ("  📊  Results  ",      results_tab),
        ]
        for label, module in _tab_defs:
            frame = ttk.Frame(self.notebook, style="Tab.TFrame", padding=16)
            self.notebook.add(frame, text=label)
            module.build(frame, self)

        # Navigation bar
        nav = ttk.Frame(main_frame, style="Card.TFrame", padding=(0, 10, 0, 2))
        nav.grid(row=1, column=0, sticky="ew")
        self.back_button = ttk.Button(
            nav, text="← Back", command=self.prev_step,
            state="disabled", style="Secondary.TButton",
        )
        self.back_button.pack(side="left")
        self.next_button = ttk.Button(
            nav, text="Next →", command=self.next_step,
            style="Primary.TButton",
        )
        self.next_button.pack(side="right")

        # Status bar
        self.status_bar = tk.Label(
            self, text="  Ready",
            bg=C_HEADER, fg=C_WHITE,
            font=("Segoe UI", 9), anchor="w",
            relief="flat", padx=10, pady=4,
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")

        # Shared state
        self.all_jobs: list[dict] = []
        self._current_apply_link: str | None = None
        self._current_glassdoor_link: str | None = None
        self._all_display_jobs: list[dict] = []
        self._filter_after_id = None

        self.load_config()
        self.after(800, self.check_for_updates)

    # ── Header ─────────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=C_HEADER, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.columnconfigure(0, weight=1)
        tk.Label(hdr, text="🔍  AI-Powered Job Search",
                 bg=C_HEADER, fg=C_WHITE,
                 font=("Segoe UI", 16, "bold"), anchor="w", padx=18,
                 ).grid(row=0, column=0, sticky="w", pady=(10, 0))
        tk.Label(hdr, text="  Find visa-sponsored roles that match your CV",
                 bg=C_HEADER, fg="#A8B8D0",
                 font=("Segoe UI", 9), anchor="w", padx=18,
                 ).grid(row=1, column=0, sticky="w")

    # ── Status helpers (thread-safe) ───────────────────────────────────────────

    def _set_status(self, text: str, color: str | None = None) -> None:
        self.after(0, lambda: self.status_bar.config(
            text=f"  {text}", fg=color or C_WHITE))

    def _log(self, text: str) -> None:
        def _do() -> None:
            self.results_text.configure(state="normal")
            self.results_text.insert("end", text)
            self.results_text.see("end")
            self.results_text.configure(state="disabled")
        self.after(0, _do)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def next_step(self) -> None:
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            self.save_config()
        if idx == 3:
            if not self.run_search():
                return
        if idx < self.notebook.index("end") - 1:
            self.notebook.select(idx + 1)
        self.update_buttons()

    def prev_step(self) -> None:
        idx = self.notebook.index(self.notebook.select())
        if idx > 0:
            self.notebook.select(idx - 1)
        self.update_buttons()

    def update_buttons(self) -> None:
        idx  = self.notebook.index(self.notebook.select())
        last = self.notebook.index("end") - 1
        self.back_button.config(state="disabled" if idx == 0 else "normal")
        if idx == last:
            self.next_button.config(text="Finish", command=self.destroy)
        elif idx == 3:
            self.next_button.config(text="🔍  Search", command=self.next_step)
        else:
            self.next_button.config(text="Next →", command=self.next_step)

    # ── Config persistence ──────────────────────────────────────────────────────

    def load_config(self) -> None:
        self.output_folder_entry.insert(0, job_search.get_default_output_folder())
        cfg = _load_cfg(CONFIG_FILE)
        if not cfg:
            return
        self.api_key_entry.insert(0, cfg.get("api_key", ""))
        self.cv_path_entry.insert(0, cfg.get("cv_path", ""))
        self.job_title_entry.insert(0, cfg.get("job_title", ""))

        # Preferences
        skills_section = cfg.get("skills_section", "").strip()
        if skills_section:
            self.skills_section_entry.delete(0, "end")
            self.skills_section_entry.insert(0, skills_section)
        locations = cfg.get("location", [])
        if locations:
            self.country_selector.set_selection(locations)
        self.visa_priority_var.set(cfg.get("visa_priority", True))
        self.remote_priority_var.set(cfg.get("remote_priority", False))

        # Restore saved skills so the user doesn't need to re-extract every session
        saved_skills = cfg.get("skills", "").strip()
        if saved_skills:
            self.skills_text.delete("1.0", "end")
            self.skills_text.insert("end", saved_skills)

        saved_folder = cfg.get("output_folder", "").strip()
        if saved_folder:
            self.output_folder_entry.delete(0, "end")
            self.output_folder_entry.insert(0, saved_folder)
        self.output_format_combobox.set(cfg.get("output_format", "Excel"))

        if self.cv_path_entry.get():
            self.after(300, self.preview_cv)

    def save_config(self) -> None:
        _save_cfg({
            "api_key":           self.api_key_entry.get().strip(),
            "cv_path":           self.cv_path_entry.get().strip(),
            "job_title":         self.job_title_entry.get().strip(),
            "skills_section":    self.skills_section_entry.get().strip(),
            "location":          self.country_selector.get_selection(),
            "visa_priority":     self.visa_priority_var.get(),
            "remote_priority":   self.remote_priority_var.get(),
            "skills":            self.skills_text.get("1.0", "end").strip(),
            "output_folder":     self.output_folder_entry.get().strip(),
            "output_format":     self.output_format_combobox.get().strip(),
        }, CONFIG_FILE)

    # ── File browsing ───────────────────────────────────────────────────────────

    def browse_cv(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CV Files", "*.pdf *.docx"), ("All Files", "*.*")])
        if path:
            self.cv_path_entry.delete(0, "end")
            self.cv_path_entry.insert(0, path)
            self.save_config()
            self.preview_cv()

    def browse_output_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_entry.delete(0, "end")
            self.output_folder_entry.insert(0, folder)
            self.save_config()

    # ── CV Preview ──────────────────────────────────────────────────────────────

    def preview_cv(self) -> None:
        path = self.cv_path_entry.get().strip()
        if not path or not os.path.exists(path):
            return
        if path.lower().endswith(".pdf"):
            text = job_search.extract_text_from_pdf(path)
        elif path.lower().endswith(".docx"):
            text = _extract_text_from_docx(path)
        else:
            messagebox.showerror("Unsupported Format", "Please select a PDF or DOCX file.")
            return
        if not text:
            messagebox.showerror("Preview Error",
                                 "Could not extract text from the CV file.")
            return
        self.cv_preview_text.configure(state="normal")
        self.cv_preview_text.delete("1.0", "end")
        self.cv_preview_text.insert("end", text)
        self.cv_preview_text.configure(state="disabled")
        self._set_status("CV preview loaded.")

    # ── Skills extraction ───────────────────────────────────────────────────────

    def extract_skills(self) -> None:
        path = self.cv_path_entry.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("No CV", "Please select a CV file in the Configuration tab.")
            return
        section = self.skills_section_entry.get().strip() or "Skills"
        if path.lower().endswith(".pdf"):
            text = job_search.extract_text_from_pdf(path)
        elif path.lower().endswith(".docx"):
            text = _extract_text_from_docx(path)
        else:
            messagebox.showerror("Unsupported Format", "Please select a PDF or DOCX file.")
            return
        if not text:
            messagebox.showerror("Error", "Failed to read text from CV.")
            return
        skills = job_search.extract_skills_from_specified_section(text, section)
        if not skills:
            messagebox.showinfo(
                "No Skills Found",
                f"No skills found in the '{section}' section.\n\n"
                "Check that the section name in Preferences matches your CV exactly.",
            )
            return
        self.skills_text.delete("1.0", "end")
        self.skills_text.insert("end", "\n".join(sorted(skills)))
        self._set_status(f"Extracted {len(skills)} skills from CV.")

    # ── Validation ──────────────────────────────────────────────────────────────

    def _validate_search_inputs(self) -> bool:
        if not self.api_key_entry.get().strip():
            messagebox.showerror("Missing API Key",
                                 "Please enter your SerpAPI key in the Configuration tab.")
            self.notebook.select(0)
            return False
        cv = self.cv_path_entry.get().strip()
        if not cv or not os.path.exists(cv):
            messagebox.showerror("Missing CV",
                                 "CV file not found. Please check the path in Configuration.")
            self.notebook.select(0)
            return False
        if not self.country_selector.get_selection():
            messagebox.showerror("No Location Selected",
                                 "Please select at least one target country in Preferences.")
            self.notebook.select(1)
            return False
        if not self.skills_text.get("1.0", "end").strip():
            messagebox.showerror("No Skills",
                                 "No skills found.\n"
                                 "Please go to the Skills tab and click 'Extract from CV'.")
            self.notebook.select(3)
            return False
        return True

    # ── Search ──────────────────────────────────────────────────────────────────

    def run_search(self) -> bool:
        """Start search in a background thread. Returns False if validation fails."""
        if not self._validate_search_inputs():
            return False
        self.all_jobs = []
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        self.preview_frame.grid_remove()
        self.log_frame.grid()
        self.view_toggle_btn.configure(text="📊  Show Results")
        self.progressbar["value"] = 0
        self.save_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.back_button.config(state="disabled")
        threading.Thread(target=self._search_worker, daemon=True).start()
        return True

    def _search_worker(self) -> None:
        try:
            skills    = [s for s in self.skills_text.get("1.0", "end").strip().splitlines()
                         if s.strip()]
            api_key   = self.api_key_entry.get().strip()
            job_title = self.job_title_entry.get().strip()
            locations = self.country_selector.get_selection()

            preferences = {
                "visa_priority":    self.visa_priority_var.get(),
                "remote_only":      self.remote_priority_var.get(),
                "target_countries": [loc.lower() for loc in locations],
                "skill_focus":      skills,
            }

            queries = job_search.search_jobs_with_visa_focus(skills, preferences)
            if job_title:
                queries.insert(0, job_title)

            self._log(f"Starting search — {len(queries)} queries planned…\n\n")
            self.after(0, lambda: self.progressbar.configure(maximum=max(len(queries), 1)))

            seen: set[str] = set()
            location_param = locations[0] if len(locations) == 1 else None

            for i, query in enumerate(queries):
                self._set_status(f"Searching: {query} …")
                self._log(f"  [{i+1}/{len(queries)}]  {query}\n")
                jobs_raw = job_search.search_jobs_on_serpapi(
                    query, api_key, location_filter=location_param)
                self.after(0, lambda v=i + 1: self.progressbar.configure(value=v))

                for job in jobs_raw:
                    jid = (f"{job.get('title','')}-"
                           f"{job.get('company_name','')}-"
                           f"{job.get('location','')}")
                    if jid in seen:
                        continue
                    seen.add(jid)
                    score, reasons = job_search.calculate_job_score(job, skills, preferences)
                    if score > 0:
                        self.all_jobs.append(
                            job_search.format_job_data(job, query, score, reasons))

            if not self.all_jobs:
                self._log("\n❌  No matching jobs found. Try adjusting skills or preferences.\n")
                self._set_status("No matching jobs found.")
                return

            divider = "─" * 56
            self._log(f"\n{divider}\n✅  Found {len(self.all_jobs)} relevant jobs!"
                      f"\n{divider}\n\nTOP MATCHES:\n\n")
            for job in sorted(self.all_jobs, key=lambda x: x["Relevance Score"],
                              reverse=True)[:5]:
                self._log(f"  🏢  {job['Job Title']} — {job['Company']}\n")
                self._log(f"      📍 {job['Location']}   |   Score: {job['Relevance Score']}\n")
                self._log(f"      {job['Score Reasons']}\n\n")

            self._set_status(
                f"✅  Search complete — {len(self.all_jobs)} jobs found.", color="#7EE8A2")

            self.after(0, lambda: results_tab.populate_results(self, self.all_jobs))
            results_tab.switch_to_preview(self)
            self.after(0, lambda: self.save_button.config(state="normal"))
            self.after(0, lambda: messagebox.showinfo(
                "Search Complete!",
                f"Found {len(self.all_jobs)} relevant jobs.\n\n"
                "Browse results in the preview panel, or click 'Save Results' to export."))

        except Exception as exc:
            self._log(f"\n❌  Error: {exc}\n")
            self._set_status(f"Error: {exc}")
        finally:
            self.after(0, lambda: self.next_button.config(state="normal"))
            self.after(0, lambda: self.back_button.config(state="normal"))
            self.after(0, self.update_buttons)

    # ── Auto-update ─────────────────────────────────────────────────────────────

    def check_for_updates(self) -> None:
        try:
            resp = requests.get(VERSION_URL, timeout=5)
            if resp.status_code != 200:
                return
            info   = resp.json()
            latest = info.get("version", "")
            dl_url = info.get("url", "")

            def _ver(v: str) -> tuple:
                try:
                    return tuple(int(x) for x in v.split("."))
                except ValueError:
                    return (0,)

            if not latest or not dl_url or _ver(latest) <= _ver(VERSION):
                return

            if not messagebox.askyesno(
                    "Update Available",
                    f"Version {latest} is available (you have {VERSION}).\n\n"
                    "Download and install now?"):
                return

            self._set_status("Downloading update…")
            dl = requests.get(dl_url, timeout=120)
            dl.raise_for_status()

            if getattr(sys, "frozen", False):
                fd, new_exe = tempfile.mkstemp(suffix=".exe")
                with os.fdopen(fd, "wb") as fh:
                    fh.write(dl.content)
                bat = (
                    "@echo off\n"
                    "ping 127.0.0.1 -n 3 > nul\n"
                    f'move /y "{new_exe}" "{sys.executable}"\n'
                    f'start "" "{sys.executable}"\n'
                    'del "%~f0"\n'
                )
                fd2, bat_path = tempfile.mkstemp(suffix=".bat")
                with os.fdopen(fd2, "w") as fh:
                    fh.write(bat)
                subprocess.Popen(["cmd", "/c", bat_path], close_fds=True)
                self.destroy()
            else:
                import shutil
                fd, tmp = tempfile.mkstemp(suffix=".py")
                with os.fdopen(fd, "wb") as fh:
                    fh.write(dl.content)
                shutil.move(tmp, sys.argv[0])
                subprocess.Popen([sys.executable] + sys.argv)
                self.destroy()

        except requests.exceptions.ConnectionError:
            pass
        except Exception as exc:
            print(f"Update check failed: {exc}")
