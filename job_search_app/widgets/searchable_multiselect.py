"""Searchable multi-select widget."""
import tkinter as tk
from tkinter import ttk


class SearchableMultiSelect(ttk.Frame):
    """A filterable multi-select listbox with a selection count badge.

    Features:
        - Live search field narrows the list as you type
        - Selections are preserved even when filtered out of view
        - Shows "N countries selected" count below the list
        - "Clear all" button
        - Fires <<SelectionChanged>> virtual event on any change

    Public API:
        .get_selection() -> list[str]   — currently selected items (sorted)
        .set_selection(items)           — programmatically select items
    """

    def __init__(self, master, items: list | None = None, height: int = 8, **kw):
        super().__init__(master, style="Tab.TFrame", **kw)
        self._all_items: list[str] = sorted(items or [])
        self._selected: set[str]  = set()
        self._displayed: list[str] = list(self._all_items)
        self._build(height)

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self, height: int) -> None:
        from job_search_app.constants import C_WHITE, C_TEXT, C_ACCENT, C_BORDER

        self.columnconfigure(0, weight=1)

        # Search row
        search_frame = ttk.Frame(self, style="Tab.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Filter:", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 6))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        ttk.Entry(search_frame, textvariable=self._search_var).grid(
            row=0, column=1, sticky="ew")

        # Listbox + scrollbar
        list_frame = ttk.Frame(self, style="Tab.TFrame")
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._listbox = tk.Listbox(
            list_frame,
            selectmode="multiple",
            height=height,
            bg=C_WHITE, fg=C_TEXT,
            selectbackground=C_ACCENT, selectforeground=C_WHITE,
            font=("Segoe UI", 10),
            borderwidth=1, relief="solid",
            highlightthickness=0,
            exportselection=False,
        )
        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                            command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=vsb.set)
        self._listbox.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # Status strip
        strip = ttk.Frame(self, style="Tab.TFrame")
        strip.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self._count_label = ttk.Label(strip, text="0 selected", style="Muted.TLabel")
        self._count_label.pack(side="left")
        ttk.Button(strip, text="Clear all", style="Small.TButton",
                   command=self._clear_all).pack(side="right")

        self._refresh_listbox()

    # ── Search / filter ───────────────────────────────────────────────────────

    def _on_search_change(self, *_) -> None:
        query = self._search_var.get().strip().lower()
        self._displayed = [i for i in self._all_items if query in i.lower()] \
            if query else list(self._all_items)
        self._refresh_listbox()

    def _refresh_listbox(self) -> None:
        """Repopulate listbox with _displayed items, re-applying selections."""
        self._listbox.delete(0, "end")
        for item in self._displayed:
            self._listbox.insert("end", item)
        for i, item in enumerate(self._displayed):
            if item in self._selected:
                self._listbox.selection_set(i)

    # ── Selection handling ────────────────────────────────────────────────────

    def _on_listbox_select(self, _event=None) -> None:
        selected_indices = set(self._listbox.curselection())
        for i, item in enumerate(self._displayed):
            if i in selected_indices:
                self._selected.add(item)
            else:
                self._selected.discard(item)
        self._update_count()
        self.event_generate("<<SelectionChanged>>")

    def _clear_all(self) -> None:
        self._selected.clear()
        self._listbox.selection_clear(0, "end")
        self._update_count()
        self.event_generate("<<SelectionChanged>>")

    def _update_count(self) -> None:
        n = len(self._selected)
        word = "country" if n == 1 else "countries"
        self._count_label.configure(text=f"{n} {word} selected")

    # ── Public API ────────────────────────────────────────────────────────────

    def get_selection(self) -> list[str]:
        return sorted(self._selected)

    def set_selection(self, items: list[str]) -> None:
        self._selected = set(items) & set(self._all_items)
        self._refresh_listbox()
        self._update_count()
