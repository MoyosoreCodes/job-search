"""Configuration tab — API key, CV path, output folder and format."""
import tkinter as tk
from tkinter import ttk
import webbrowser

from job_search_app.constants import C_WHITE, C_ACCENT


def build(parent: ttk.Frame, app) -> None:
    """Populate *parent* with Configuration tab widgets."""
    parent.columnconfigure(0, weight=1)

    lf = ttk.LabelFrame(parent, text=" API & File Settings ", padding=14)
    lf.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    lf.columnconfigure(1, weight=1)

    # SerpAPI key
    ttk.Label(lf, text="SerpAPI Key:").grid(row=0, column=0, sticky="w", pady=6)
    app.api_key_entry = ttk.Entry(lf, width=52, show="●")
    app.api_key_entry.grid(row=0, column=1, sticky="ew", pady=6, padx=6)
    app.api_key_entry.bind("<FocusOut>", lambda _: app.save_config())

    link = tk.Label(lf, text="Get API Key →",
                    fg=C_ACCENT, bg=C_WHITE, cursor="hand2",
                    font=("Segoe UI", 9, "underline"))
    link.grid(row=0, column=2, sticky="w", padx=4)
    link.bind("<Button-1>", lambda _: webbrowser.open_new("https://serpapi.com/"))

    # CV file
    ttk.Label(lf, text="CV File (PDF/DOCX):").grid(row=1, column=0, sticky="w", pady=6)
    app.cv_path_entry = ttk.Entry(lf, width=52)
    app.cv_path_entry.grid(row=1, column=1, sticky="ew", pady=6, padx=6)
    ttk.Button(lf, text="Browse", command=app.browse_cv,
               style="Small.TButton").grid(row=1, column=2, padx=4)

    # Output folder
    ttk.Label(lf, text="Output Folder:").grid(row=2, column=0, sticky="w", pady=6)
    app.output_folder_entry = ttk.Entry(lf, width=52)
    app.output_folder_entry.grid(row=2, column=1, sticky="ew", pady=6, padx=6)
    ttk.Button(lf, text="Browse", command=app.browse_output_folder,
               style="Small.TButton").grid(row=2, column=2, padx=4)

    # Output format
    ttk.Label(lf, text="Output Format:").grid(row=3, column=0, sticky="w", pady=6)
    app.output_format_combobox = ttk.Combobox(
        lf, values=["Excel", "CSV"], state="readonly", width=18)
    app.output_format_combobox.set("Excel")
    app.output_format_combobox.grid(row=3, column=1, sticky="w", pady=6, padx=6)

    ttk.Label(parent, text="💡  Your API key and CV path are saved automatically.",
              style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))
