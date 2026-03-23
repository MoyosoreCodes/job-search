"""Results tab — job list treeview, filters, and detail panel."""
import os
import webbrowser
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

import job_search
from job_search_app.constants import (
    C_BG, C_WHITE, C_TEXT,
    C_ROW_ALT, C_ROW_VISA, C_ROW_MAYBE,
    C_ROW_APPLIED, C_ROW_INTERESTED, C_ROW_REJECTED,
)
from job_search_app.status_tracker import STATUS_LABELS
from job_search_app.widgets.job_detail_panel import JobDetailPanel


# ---------------------------------------------------------------------------
# Tab builder
# ---------------------------------------------------------------------------

def build(parent: ttk.Frame, app) -> None:
    """Populate *parent* with Results tab widgets."""
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(1, weight=1)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    toolbar = ttk.Frame(parent, style="Tab.TFrame")
    toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    toolbar.columnconfigure(2, weight=1)

    app.results_count_label = ttk.Label(toolbar, text="No results yet", style="H2.TLabel")
    app.results_count_label.grid(row=0, column=0, sticky="w")

    ttk.Button(toolbar, text="📂  Load File",
               command=lambda: load_results_file(app),
               style="Small.TButton").grid(row=0, column=1, padx=(12, 4))

    app.view_toggle_btn = ttk.Button(
        toolbar, text="📋  Show Log",
        command=lambda: toggle_view(app),
        style="Secondary.TButton")
    app.view_toggle_btn.grid(row=0, column=2, sticky="w", padx=4)

    app.progressbar = ttk.Progressbar(
        toolbar, orient="horizontal", mode="determinate", length=160)
    app.progressbar.grid(row=0, column=3, padx=(0, 8))

    app.save_button = ttk.Button(
        toolbar, text="💾  Save Results",
        command=lambda: save_results(app),
        state="disabled", style="Primary.TButton")
    app.save_button.grid(row=0, column=4)

    # ── Log frame ─────────────────────────────────────────────────────────────
    app.log_frame = ttk.Frame(parent, style="Tab.TFrame")
    app.log_frame.grid(row=1, column=0, sticky="nsew")
    app.log_frame.columnconfigure(0, weight=1)
    app.log_frame.rowconfigure(0, weight=1)

    lf = ttk.LabelFrame(app.log_frame, text=" Search Log ", padding=10)
    lf.grid(row=0, column=0, sticky="nsew")
    lf.columnconfigure(0, weight=1)
    lf.rowconfigure(0, weight=1)

    log_tw = ttk.Frame(lf, style="Tab.TFrame")
    log_tw.grid(row=0, column=0, sticky="nsew")
    log_tw.columnconfigure(0, weight=1)
    log_tw.rowconfigure(0, weight=1)

    app.results_text = tk.Text(
        log_tw, font=("Segoe UI", 10), bg=C_WHITE, fg=C_TEXT,
        relief="solid", borderwidth=1, padx=8, pady=8,
        wrap="word", state="disabled",
    )
    app.results_text.grid(row=0, column=0, sticky="nsew")
    res_sb = ttk.Scrollbar(log_tw, orient="vertical", command=app.results_text.yview)
    app.results_text.configure(yscrollcommand=res_sb.set)
    res_sb.grid(row=0, column=1, sticky="ns")

    # ── Preview frame ─────────────────────────────────────────────────────────
    app.preview_frame = ttk.Frame(parent, style="Tab.TFrame")
    app.preview_frame.columnconfigure(0, weight=1)
    app.preview_frame.rowconfigure(1, weight=1)
    app.preview_frame.grid(row=1, column=0, sticky="nsew")
    app.preview_frame.grid_remove()

    # Filter / sort bar
    filter_bar = ttk.Frame(app.preview_frame, style="Tab.TFrame")
    filter_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

    ttk.Label(filter_bar, text="Filter:", style="Muted.TLabel").pack(side="left")
    app.filter_var = tk.StringVar()
    app.filter_var.trace_add("write", lambda *_: _schedule_filter(app))
    ttk.Entry(filter_bar, textvariable=app.filter_var,
              width=20).pack(side="left", padx=(4, 12))

    ttk.Label(filter_bar, text="Sort:", style="Muted.TLabel").pack(side="left")
    app.sort_var = tk.StringVar(value="Score ↓")
    sort_cb = ttk.Combobox(
        filter_bar, textvariable=app.sort_var,
        values=["Score ↓", "Score ↑", "Date ↓", "Date ↑", "Company A–Z"],
        state="readonly", width=14)
    sort_cb.pack(side="left", padx=4)
    sort_cb.bind("<<ComboboxSelected>>", lambda _: apply_filter(app))

    ttk.Label(filter_bar, text="Visa:", style="Muted.TLabel").pack(side="left", padx=(12, 0))
    app.visa_filter_var = tk.StringVar(value="All")
    visa_cb = ttk.Combobox(
        filter_bar, textvariable=app.visa_filter_var,
        values=["All", "Yes", "Maybe", "Unknown"],
        state="readonly", width=10)
    visa_cb.pack(side="left", padx=4)
    visa_cb.bind("<<ComboboxSelected>>", lambda _: apply_filter(app))

    ttk.Label(filter_bar, text="Status:", style="Muted.TLabel").pack(side="left", padx=(12, 0))
    app.status_filter_var = tk.StringVar(value="All")
    status_cb = ttk.Combobox(
        filter_bar, textvariable=app.status_filter_var,
        values=["All", "Applied", "Interested", "Rejected", "None"],
        state="readonly", width=11)
    status_cb.pack(side="left", padx=4)
    status_cb.bind("<<ComboboxSelected>>", lambda _: apply_filter(app))

    # Paned window — left list | right detail
    paned = tk.PanedWindow(
        app.preview_frame, orient="horizontal",
        bg=C_BG, sashwidth=6, sashrelief="flat", bd=0)
    paned.grid(row=1, column=0, sticky="nsew")

    # Left: treeview
    left = ttk.Frame(paned, style="Tab.TFrame")
    tree_frame = ttk.Frame(left, style="Tab.TFrame")
    tree_frame.pack(fill="both", expand=True)

    cols = ("title", "company", "location", "score", "visa", "status")
    app.jobs_tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", selectmode="browse")

    for col, heading, width, anchor in [
        ("title",    "Job Title", 180, "w"),
        ("company",  "Company",   130, "w"),
        ("location", "Location",  130, "w"),
        ("score",    "⭐",         46,  "center"),
        ("visa",     "Visa",       58,  "center"),
        ("status",   "Status",    100,  "center"),
    ]:
        app.jobs_tree.heading(col, text=heading)
        app.jobs_tree.column(col, width=width, minwidth=max(40, width - 40),
                              anchor=anchor, stretch=(col in ("title", "company", "location")))

    app.jobs_tree.tag_configure("visa_yes",          background=C_ROW_VISA)
    app.jobs_tree.tag_configure("visa_maybe",        background=C_ROW_MAYBE)
    app.jobs_tree.tag_configure("alt",               background=C_ROW_ALT)
    app.jobs_tree.tag_configure("status_applied",    background=C_ROW_APPLIED)
    app.jobs_tree.tag_configure("status_interested", background=C_ROW_INTERESTED)
    app.jobs_tree.tag_configure("status_rejected",   background=C_ROW_REJECTED)

    tree_vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=app.jobs_tree.yview)
    tree_hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=app.jobs_tree.xview)
    app.jobs_tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)
    app.jobs_tree.grid(row=0, column=0, sticky="nsew")
    tree_vsb.grid(row=0, column=1, sticky="ns")
    tree_hsb.grid(row=1, column=0, sticky="ew")
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)

    app.jobs_tree.bind("<<TreeviewSelect>>", lambda _: _on_job_select(app))
    paned.add(left, minsize=320)

    # Right: detail panel
    right = ttk.Frame(paned, style="Tab.TFrame")
    right.columnconfigure(0, weight=1)
    right.rowconfigure(0, weight=1)
    app.detail_panel = JobDetailPanel(right, app)
    app.detail_panel.grid(row=0, column=0, sticky="nsew")
    paned.add(right, minsize=400)

    # Refresh treeview when a status is changed from the detail panel
    app.bind("<<JobStatusChanged>>", lambda _: apply_filter(app))


# ---------------------------------------------------------------------------
# Event handlers (module-level functions)
# ---------------------------------------------------------------------------

def _on_job_select(app) -> None:
    sel = app.jobs_tree.selection()
    if not sel:
        return
    try:
        job = app._all_display_jobs[int(sel[0])]
        app.detail_panel.show_job(job)
    except (ValueError, IndexError):
        pass


def toggle_view(app) -> None:
    if app.preview_frame.winfo_ismapped():
        app.preview_frame.grid_remove()
        app.log_frame.grid()
        app.view_toggle_btn.configure(text="📊  Show Results")
    else:
        app.log_frame.grid_remove()
        app.preview_frame.grid()
        app.view_toggle_btn.configure(text="📋  Show Log")


def switch_to_preview(app) -> None:
    """Thread-safe: switch to results preview view."""
    def _do() -> None:
        app.log_frame.grid_remove()
        app.preview_frame.grid()
        app.view_toggle_btn.configure(text="📋  Show Log")
    app.after(0, _do)


def populate_results(app, jobs: list) -> None:
    """Set canonical job list and refresh the treeview."""
    app.all_jobs = list(jobs)
    apply_filter(app)


def _schedule_filter(app) -> None:
    if app._filter_after_id:
        app.after_cancel(app._filter_after_id)
    app._filter_after_id = app.after(250, lambda: apply_filter(app))


def apply_filter(app) -> None:
    """Re-sort and re-filter the treeview from app.all_jobs."""
    app._filter_after_id = None
    query    = app.filter_var.get().lower().strip()
    sort_by  = app.sort_var.get()
    visa_f   = app.visa_filter_var.get()
    status_f = app.status_filter_var.get()
    tracker  = app._status_tracker

    jobs = list(app.all_jobs)

    # Text filter
    if query:
        jobs = [j for j in jobs if (
            query in j.get("Job Title",     "").lower() or
            query in j.get("Company",       "").lower() or
            query in j.get("Location",      "").lower() or
            query in j.get("Score Reasons", "").lower()
        )]

    # Visa filter
    if visa_f != "All":
        jobs = [j for j in jobs
                if j.get("Visa Sponsorship Mentioned", "") == visa_f]

    # Status filter
    if status_f != "All":
        if status_f == "None":
            jobs = [j for j in jobs if not tracker.get(j)]
        else:
            jobs = [j for j in jobs if tracker.get(j) == status_f]

    # Sort
    if sort_by == "Score ↓":
        jobs.sort(key=lambda x: x.get("Relevance Score", 0), reverse=True)
    elif sort_by == "Score ↑":
        jobs.sort(key=lambda x: x.get("Relevance Score", 0))
    elif sort_by in ("Date ↓", "Date ↑"):
        reverse = (sort_by == "Date ↓")
        jobs.sort(
            key=lambda x: (
                x.get("Posting Date ISO") or
                job_search.normalize_posting_date(
                    x.get("Posting Date", "")).isoformat()
            ),
            reverse=reverse,
        )
    elif sort_by == "Company A–Z":
        jobs.sort(key=lambda x: x.get("Company", "").lower())

    app._all_display_jobs = jobs

    # Repopulate treeview
    for item in app.jobs_tree.get_children():
        app.jobs_tree.delete(item)

    for idx, job in enumerate(jobs):
        status = tracker.get(job)
        visa   = job.get("Visa Sponsorship Mentioned", "Unknown")

        if status == "Applied":
            tag = "status_applied"
        elif status == "Interested":
            tag = "status_interested"
        elif status == "Rejected":
            tag = "status_rejected"
        else:
            tag = ("visa_yes"   if visa == "Yes"
                   else "visa_maybe" if visa == "Maybe"
                   else "alt"        if idx % 2 == 0
                   else "")

        app.jobs_tree.insert(
            "", "end", iid=str(idx),
            values=(
                job.get("Job Title",   "—"),
                job.get("Company",     "—"),
                job.get("Location",    "—"),
                job.get("Relevance Score", 0),
                visa,
                STATUS_LABELS.get(status, ""),
            ),
            tags=(tag,) if tag else (),
        )

    count = len(jobs)
    total = len(app.all_jobs)
    label = f"{count} result{'s' if count != 1 else ''}"
    if count < total:
        label += f"  (filtered from {total})"
    app.results_count_label.configure(text=label)


def load_results_file(app) -> None:
    path = filedialog.askopenfilename(
        title="Open Results File",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"),
                   ("All files", "*.*")],
    )
    if not path:
        return
    try:
        df = pd.read_csv(path) if path.lower().endswith(".csv") \
            else pd.read_excel(path, engine="openpyxl")
        df = df.fillna("")
        normalised = []
        for job in df.to_dict(orient="records"):
            nj = {str(k).strip(): str(v).strip() for k, v in job.items()}
            try:
                nj["Relevance Score"] = int(float(nj.get("Relevance Score", 0)))
            except (ValueError, TypeError):
                nj["Relevance Score"] = 0
            normalised.append(nj)

        populate_results(app, normalised)
        switch_to_preview(app)
        app.save_button.configure(state="normal")
        app._set_status(f"Loaded {len(normalised)} jobs from file.")
        app.results_count_label.configure(text=f"{len(normalised)} results  (from file)")
        app.notebook.select(4)

    except Exception as exc:
        messagebox.showerror("Load Error", f"Could not load file:\n{exc}")


def save_results(app) -> None:
    if not app.all_jobs:
        messagebox.showwarning("No Results", "There are no results to save.")
        return

    folder = app.output_folder_entry.get().strip()
    if not folder:
        folder = job_search.get_default_output_folder()
        app.output_folder_entry.delete(0, "end")
        app.output_folder_entry.insert(0, folder)
        app.save_config()

    fmt = app.output_format_combobox.get().strip()
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "xlsx" if fmt == "Excel" else "csv"
    out = os.path.join(folder, f"job_search_result_{ts}.{ext}")

    try:
        os.makedirs(folder, exist_ok=True)
        df = pd.DataFrame(app.all_jobs)
        # Strip internal-only columns before writing to disk
        export_df = df.drop(
            columns=["_full_description", "Posting Date ISO"], errors="ignore")
        export_df = export_df.sort_values(
            ["Relevance Score", "Posting Date"], ascending=[False, False])
        if fmt == "Excel":
            export_df.to_excel(out, index=False, engine="openpyxl")
        else:
            export_df.to_csv(out, index=False)
        messagebox.showinfo("Saved!", f"Results saved to:\n{out}")
        app._set_status(f"Saved: {out}")
        webbrowser.open(os.path.dirname(out))
    except Exception as exc:
        messagebox.showerror("Save Error", f"Could not save file:\n{exc}")
