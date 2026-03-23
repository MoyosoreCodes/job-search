"""Preferences tab — job title, searchable country selector, search priorities."""
import tkinter as tk
from tkinter import ttk

from job_search_app.constants import COUNTRIES
from job_search_app.widgets.searchable_multiselect import SearchableMultiSelect


def build(parent: ttk.Frame, app) -> None:
    """Populate *parent* with Preferences tab widgets."""
    parent.columnconfigure(0, weight=1)

    pf = ttk.LabelFrame(parent, text=" Job Preferences ", padding=14)
    pf.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    pf.columnconfigure(1, weight=1)

    # Job title
    ttk.Label(pf, text="Your Job Title:").grid(row=0, column=0, sticky="w", pady=6)
    app.job_title_entry = ttk.Entry(pf, width=52)
    app.job_title_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=6, padx=6)

    # Skills section name
    ttk.Label(pf, text="Skills Section Name:").grid(row=1, column=0, sticky="w", pady=6)
    app.skills_section_entry = ttk.Entry(pf, width=28)
    app.skills_section_entry.insert(0, "Skills")
    app.skills_section_entry.grid(row=1, column=1, sticky="w", pady=6, padx=6)
    ttk.Label(pf, text="(as it appears in your CV)",
              style="Muted.TLabel").grid(row=1, column=2, sticky="w")

    # Searchable country multi-select
    ttk.Label(pf, text="Target Countries:").grid(row=2, column=0, sticky="nw", pady=6)
    app.country_selector = SearchableMultiSelect(pf, items=COUNTRIES, height=8)
    app.country_selector.grid(row=2, column=1, columnspan=2, sticky="ew", pady=6, padx=6)
    app.country_selector.bind("<<SelectionChanged>>", lambda _: app.save_config())

    # Search priorities
    priof = ttk.LabelFrame(parent, text=" Search Priorities ", padding=14)
    priof.grid(row=1, column=0, sticky="ew", pady=6)

    app.visa_priority_var   = tk.BooleanVar(value=True)
    app.remote_priority_var = tk.BooleanVar()
    app.visa_priority_var.trace_add("write",   lambda *_: app.save_config())
    app.remote_priority_var.trace_add("write",  lambda *_: app.save_config())

    ttk.Checkbutton(priof, text="🌍  Prioritise visa sponsorship opportunities",
                    variable=app.visa_priority_var,
                    ).grid(row=0, column=0, sticky="w", padx=6, pady=4)
    ttk.Checkbutton(priof, text="💻  Include remote work opportunities",
                    variable=app.remote_priority_var,
                    ).grid(row=1, column=0, sticky="w", padx=6, pady=4)
