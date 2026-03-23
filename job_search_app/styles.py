"""ttk style configuration for the application."""
from tkinter import ttk

from job_search_app.constants import (
    C_BG, C_HEADER, C_ACCENT, C_ACCENT_DK, C_SUCCESS,
    C_TEXT, C_MUTED, C_WHITE, C_BORDER,
)


def apply_styles(root) -> None:
    """Configure all ttk styles on *root*."""
    s = ttk.Style(root)
    s.theme_use("clam")

    s.configure(".",           background=C_BG,    foreground=C_TEXT, font=("Segoe UI", 10))
    s.configure("Card.TFrame", background=C_WHITE)
    s.configure("Tab.TFrame",  background=C_WHITE)
    s.configure("TFrame",      background=C_BG)

    # Notebook tabs
    s.configure("TNotebook",
                background=C_HEADER, borderwidth=0, tabmargins=[0, 0, 0, 0])
    s.configure("TNotebook.Tab",
                background=C_HEADER, foreground="#A8B8D0",
                font=("Segoe UI", 9, "bold"), padding=[14, 8], borderwidth=0)
    s.map("TNotebook.Tab",
          background=[("selected", C_ACCENT), ("active", "#243A5E")],
          foreground=[("selected", C_WHITE),  ("active", C_WHITE)])

    # Labels
    s.configure("TLabel",       background=C_WHITE, foreground=C_TEXT,  font=("Segoe UI", 10))
    s.configure("Muted.TLabel", background=C_WHITE, foreground=C_MUTED, font=("Segoe UI", 9))
    s.configure("H2.TLabel",    background=C_WHITE, foreground=C_TEXT,  font=("Segoe UI", 11, "bold"))

    # LabelFrame
    s.configure("TLabelframe",
                background=C_WHITE, bordercolor=C_BORDER, relief="solid", borderwidth=1)
    s.configure("TLabelframe.Label",
                background=C_WHITE, foreground=C_HEADER, font=("Segoe UI", 10, "bold"))

    # Buttons — Primary (blue)
    s.configure("Primary.TButton",
                background=C_ACCENT, foreground=C_WHITE,
                font=("Segoe UI", 10, "bold"), padding=[14, 7],
                borderwidth=0, relief="flat")
    s.map("Primary.TButton",
          background=[("active", C_ACCENT_DK), ("disabled", "#BDC3C7")],
          foreground=[("disabled", "#ECF0F1")])

    # Buttons — Secondary (grey)
    s.configure("Secondary.TButton",
                background="#E8ECF0", foreground=C_TEXT,
                font=("Segoe UI", 10), padding=[14, 7],
                borderwidth=0, relief="flat")
    s.map("Secondary.TButton",
          background=[("active", "#D0D7E0"), ("disabled", "#F0F0F0")])

    # Buttons — Small inline
    s.configure("Small.TButton",
                background=C_ACCENT, foreground=C_WHITE,
                font=("Segoe UI", 9), padding=[8, 4],
                borderwidth=0, relief="flat")
    s.map("Small.TButton", background=[("active", C_ACCENT_DK)])

    # Buttons — Success (green)
    s.configure("Success.TButton",
                background=C_SUCCESS, foreground=C_WHITE,
                font=("Segoe UI", 10, "bold"), padding=[14, 7],
                borderwidth=0, relief="flat")
    s.map("Success.TButton",
          background=[("active", "#1E8449"), ("disabled", "#BDC3C7")])

    # Entry / Combobox
    s.configure("TEntry",
                fieldbackground=C_WHITE, foreground=C_TEXT,
                bordercolor=C_BORDER, lightcolor=C_BORDER,
                darkcolor=C_BORDER, borderwidth=1, padding=5)
    s.configure("TCombobox",
                fieldbackground=C_WHITE, foreground=C_TEXT,
                bordercolor=C_BORDER, padding=5)

    # Checkbutton
    s.configure("TCheckbutton", background=C_WHITE, foreground=C_TEXT, font=("Segoe UI", 10))

    # Progressbar
    s.configure("Horizontal.TProgressbar",
                troughcolor=C_BORDER, background=C_ACCENT,
                borderwidth=0, thickness=8)

    # Scrollbar
    s.configure("TScrollbar",
                background=C_BORDER, troughcolor=C_BG,
                borderwidth=0, arrowsize=12)

    # Treeview
    s.configure("Treeview",
                background=C_WHITE, foreground=C_TEXT,
                fieldbackground=C_WHITE, rowheight=28,
                font=("Segoe UI", 9), borderwidth=0)
    s.configure("Treeview.Heading",
                background=C_HEADER, foreground=C_WHITE,
                font=("Segoe UI", 9, "bold"), padding=[6, 5])
    s.map("Treeview",
          background=[("selected", C_ACCENT)],
          foreground=[("selected", C_WHITE)])
