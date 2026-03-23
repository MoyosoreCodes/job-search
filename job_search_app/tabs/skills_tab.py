"""Skills tab — editable list of skills for the job search."""
import tkinter as tk
from tkinter import ttk

from job_search_app.constants import C_WHITE, C_TEXT


def build(parent: ttk.Frame, app) -> None:
    """Populate *parent* with Skills tab widgets."""
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(1, weight=1)

    hrow = ttk.Frame(parent, style="Tab.TFrame")
    hrow.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    ttk.Label(hrow, text="Extracted Skills", style="H2.TLabel").pack(side="left")
    ttk.Label(hrow, text="  (edit to add / remove skills)",
              style="Muted.TLabel").pack(side="left")
    ttk.Button(hrow, text="⚙  Extract from CV", command=app.extract_skills,
               style="Small.TButton").pack(side="right")

    tw = ttk.Frame(parent, style="Tab.TFrame")
    tw.grid(row=1, column=0, sticky="nsew")
    tw.columnconfigure(0, weight=1)
    tw.rowconfigure(0, weight=1)

    app.skills_text = tk.Text(
        tw, font=("Segoe UI", 10), bg=C_WHITE, fg=C_TEXT,
        relief="solid", borderwidth=1, padx=8, pady=8, wrap="word",
    )
    app.skills_text.grid(row=0, column=0, sticky="nsew")
    app.skills_text.bind("<FocusOut>", lambda _: app.save_config())
    sb = ttk.Scrollbar(tw, orient="vertical", command=app.skills_text.yview)
    app.skills_text.configure(yscrollcommand=sb.set)
    sb.grid(row=0, column=1, sticky="ns")

    ttk.Label(parent, text="💡  One skill per line. Click 'Search' when ready.",
              style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
