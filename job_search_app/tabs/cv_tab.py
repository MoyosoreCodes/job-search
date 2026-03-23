"""CV Preview tab — shows extracted text from the uploaded CV."""
import tkinter as tk
from tkinter import ttk

from job_search_app.constants import C_WHITE, C_TEXT


def build(parent: ttk.Frame, app) -> None:
    """Populate *parent* with CV Preview tab widgets."""
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(1, weight=1)

    hrow = ttk.Frame(parent, style="Tab.TFrame")
    hrow.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    ttk.Label(hrow, text="CV Preview", style="H2.TLabel").pack(side="left")
    ttk.Label(hrow, text="  (extracted text from your CV)",
              style="Muted.TLabel").pack(side="left")
    ttk.Button(hrow, text="⟳  Refresh", command=app.preview_cv,
               style="Small.TButton").pack(side="right")

    tw = ttk.Frame(parent, style="Tab.TFrame")
    tw.grid(row=1, column=0, sticky="nsew")
    tw.columnconfigure(0, weight=1)
    tw.rowconfigure(0, weight=1)

    app.cv_preview_text = tk.Text(
        tw, font=("Segoe UI", 10), bg=C_WHITE, fg=C_TEXT,
        relief="solid", borderwidth=1, padx=8, pady=8,
        wrap="word", state="disabled",
    )
    app.cv_preview_text.grid(row=0, column=0, sticky="nsew")
    sb = ttk.Scrollbar(tw, orient="vertical", command=app.cv_preview_text.yview)
    app.cv_preview_text.configure(yscrollcommand=sb.set)
    sb.grid(row=0, column=1, sticky="ns")
