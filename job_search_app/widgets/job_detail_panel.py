"""Job detail panel — rich display for a selected job with action buttons."""
import tkinter as tk
from tkinter import ttk
import webbrowser

from job_search_app.constants import (
    C_WHITE, C_TEXT, C_HEADER, C_ACCENT, C_SUCCESS, C_WARN, C_MUTED, C_BORDER,
)
from job_search_app.status_tracker import StatusTracker, STATUS_LABELS


class JobDetailPanel(ttk.Frame):
    """Right-side panel showing full details and actions for one job.

    Widget references assigned on *app*:
        app.apply_btn, app.glassdoor_btn, app.copy_link_btn
        app.detail_text
        app._current_apply_link, app._current_glassdoor_link
        app._status_tracker
    """

    def __init__(self, master, app, **kw) -> None:
        super().__init__(master, style="Tab.TFrame", **kw)
        self._app = app
        self._tracker = StatusTracker()
        self._current_job: dict | None = None
        app._status_tracker = self._tracker

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_action_bar()
        self._build_detail_area()
        self.show_placeholder()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_action_bar(self) -> None:
        bar = ttk.Frame(self, style="Tab.TFrame")
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._apply_btn = ttk.Button(
            bar, text="🔗  Apply Now",
            command=self._open_apply_link,
            style="Success.TButton", state="disabled",
        )
        self._apply_btn.pack(side="left", padx=(0, 8))
        self._app.apply_btn = self._apply_btn

        self._glassdoor_btn = ttk.Button(
            bar, text="🔍  Glassdoor",
            command=self._open_glassdoor,
            style="Secondary.TButton", state="disabled",
        )
        self._glassdoor_btn.pack(side="left", padx=(0, 8))
        self._app.glassdoor_btn = self._glassdoor_btn

        self._copy_btn = ttk.Button(
            bar, text="📋  Copy Link",
            command=self._copy_apply_link,
            style="Secondary.TButton", state="disabled",
        )
        self._copy_btn.pack(side="left")
        self._app.copy_link_btn = self._copy_btn

        # Status buttons
        ttk.Separator(bar, orient="vertical").pack(side="left", padx=(12, 8), fill="y")

        self._status_btns: dict[str, ttk.Button] = {}
        for val, label in [("Applied", "🟢 Applied"), ("Interested", "⭐ Interested"),
                           ("Rejected", "❌ Rejected"), ("", "⬜ Clear")]:
            btn = ttk.Button(
                bar, text=label, state="disabled",
                command=lambda v=val: self._set_job_status(v),
                style="Secondary.TButton",
            )
            btn.pack(side="left", padx=(0, 4))
            self._status_btns[val] = btn

    def _build_detail_area(self) -> None:
        wrap = ttk.Frame(self, style="Tab.TFrame")
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)

        self._text = tk.Text(
            wrap, font=("Segoe UI", 10), bg=C_WHITE, fg=C_TEXT,
            relief="solid", borderwidth=1, padx=14, pady=12,
            wrap="word", state="disabled", cursor="arrow",
        )
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self._text.yview)
        self._text.configure(yscrollcommand=vsb.set)
        self._text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._app.detail_text = self._text

        # Text tags
        self._text.tag_configure(
            "title", font=("Segoe UI", 14, "bold"), foreground=C_HEADER,
            spacing1=4, spacing3=4)
        self._text.tag_configure(
            "company", font=("Segoe UI", 11, "bold"), foreground=C_ACCENT)
        self._text.tag_configure(
            "divider", foreground=C_BORDER, font=("Segoe UI", 9))
        self._text.tag_configure(
            "meta_key", font=("Segoe UI", 9, "bold"), foreground=C_MUTED, spacing1=2)
        self._text.tag_configure(
            "meta_val", font=("Segoe UI", 10), foreground=C_TEXT)
        self._text.tag_configure(
            "visa_yes",   font=("Segoe UI", 10, "bold"), foreground=C_SUCCESS)
        self._text.tag_configure(
            "visa_maybe", font=("Segoe UI", 10, "bold"), foreground=C_WARN)
        self._text.tag_configure(
            "visa_no",    font=("Segoe UI", 10), foreground=C_MUTED)
        self._text.tag_configure(
            "section", font=("Segoe UI", 10, "bold"),
            foreground=C_HEADER, spacing1=10, spacing3=4)
        self._text.tag_configure(
            "body", font=("Segoe UI", 10), foreground=C_TEXT,
            spacing1=2, lmargin1=8, lmargin2=8)
        self._text.tag_configure(
            "link", font=("Segoe UI", 9), foreground=C_ACCENT, underline=True)
        self._text.tag_configure(
            "score_high", font=("Segoe UI", 10, "bold"), foreground=C_SUCCESS)
        self._text.tag_configure(
            "score_mid",  font=("Segoe UI", 10, "bold"), foreground=C_WARN)
        self._text.tag_configure(
            "score_low",  font=("Segoe UI", 10), foreground=C_MUTED)
        self._text.tag_configure(
            "status_val", font=("Segoe UI", 10, "bold"), foreground=C_ACCENT)

    # ── Public methods ────────────────────────────────────────────────────────

    def show_placeholder(self) -> None:
        self._write(lambda t: t.insert(
            "end",
            "\n\n        ← Select a job from the list to see full details.\n\n"
            "        You can also click 📂 Load File to review a\n"
            "        previously saved Excel or CSV result file.",
            "meta_key",
        ))

    def show_job(self, job: dict) -> None:
        self._current_job = job
        apply_link     = job.get("Application Link", "Not available")
        glassdoor_link = job.get("Company Glassdoor", "")
        self._app._current_apply_link     = apply_link if apply_link != "Not available" else None
        self._app._current_glassdoor_link = (
            glassdoor_link if glassdoor_link not in ("", "Not available") else None)

        def _render(t: tk.Text) -> None:
            t.insert("end", job.get("Job Title", "—") + "\n", "title")
            t.insert("end", f"🏢  {job.get('Company', '—')}", "company")
            t.insert("end", f"   📍 {job.get('Location', '—')}\n", "meta_val")
            t.insert("end", "─" * 60 + "\n", "divider")

            visa  = job.get("Visa Sponsorship Mentioned", "Unknown")
            score = job.get("Relevance Score", 0)

            for key, val in [
                ("📅  Posted:   ", job.get("Posting Date", "Unknown")),
                ("💰  Salary:   ", job.get("Salary", "Not specified")),
            ]:
                t.insert("end", key, "meta_key")
                t.insert("end", f"{val}\n", "meta_val")

            t.insert("end", "✅  Visa:     ", "meta_key")
            if visa == "Yes":
                t.insert("end", "Sponsorship confirmed\n", "visa_yes")
            elif visa == "Maybe":
                t.insert("end", "Sponsor-friendly location\n", "visa_maybe")
            else:
                t.insert("end", "Not mentioned\n", "visa_no")

            t.insert("end", "⭐  Score:    ", "meta_key")
            tag = "score_high" if score >= 150 else "score_mid" if score >= 80 else "score_low"
            t.insert("end", f"{score}\n", tag)

            t.insert("end", "🔍  Query:    ", "meta_key")
            t.insert("end", f"{job.get('Search Query', '—')}\n", "meta_val")
            t.insert("end", "💡  Reasons:  ", "meta_key")
            t.insert("end", f"{job.get('Score Reasons', '—')}\n", "meta_val")

            status = self._tracker.get(job)
            if status:
                t.insert("end", "📌  Status:   ", "meta_key")
                t.insert("end", f"{STATUS_LABELS.get(status, status)}\n", "status_val")

            t.insert("end", "🔗  Apply:    ", "meta_key")
            if apply_link and apply_link != "Not available":
                t.insert("end", apply_link + "\n", "link")
            else:
                t.insert("end", "Not available\n", "visa_no")

            t.insert("end", "🏷  Glassdoor: ", "meta_key")
            if glassdoor_link and glassdoor_link != "Not available":
                t.insert("end", glassdoor_link + "\n", "link")
            else:
                t.insert("end", "Not available\n", "visa_no")

            t.insert("end", "\n" + "─" * 60 + "\n", "divider")
            t.insert("end", "DESCRIPTION\n", "section")
            description = (job.get("_full_description")
                           or job.get("Job Description", "No description available."))
            t.insert("end", description + "\n", "body")

        self._write(_render)

        self._apply_btn.configure(
            state="normal" if self._app._current_apply_link else "disabled")
        self._glassdoor_btn.configure(
            state="normal" if self._app._current_glassdoor_link else "disabled")
        self._copy_btn.configure(
            state="normal" if self._app._current_apply_link else "disabled")
        for btn in self._status_btns.values():
            btn.configure(state="normal")

    # ── Status handling ───────────────────────────────────────────────────────

    def _set_job_status(self, status: str) -> None:
        if not self._current_job:
            return
        self._tracker.set(self._current_job, status)
        self._app.event_generate("<<JobStatusChanged>>")
        self.show_job(self._current_job)

    # ── Link actions ──────────────────────────────────────────────────────────

    def _open_apply_link(self) -> None:
        if self._app._current_apply_link:
            webbrowser.open_new(self._app._current_apply_link)

    def _open_glassdoor(self) -> None:
        if self._app._current_glassdoor_link:
            webbrowser.open_new(self._app._current_glassdoor_link)

    def _copy_apply_link(self) -> None:
        if self._app._current_apply_link:
            self._app.clipboard_clear()
            self._app.clipboard_append(self._app._current_apply_link)
            self._app._set_status("Application link copied to clipboard.")

    # ── Helper ────────────────────────────────────────────────────────────────

    def _write(self, fn) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        fn(self._text)
        self._text.configure(state="disabled")
        self._text.see("1.0")
