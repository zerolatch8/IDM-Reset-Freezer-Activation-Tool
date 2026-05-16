"""
Sidebar navigation component.

Windows 11 File Explorer-inspired sidebar with icon + label items
and a colored active indicator bar.
"""

import customtkinter as ctk
from typing import Callable, Optional

from app.gui.theme import Colors, Fonts, Spacing


class SidebarItem(ctk.CTkFrame):
    """A single clickable sidebar navigation item."""

    def __init__(
        self,
        master,
        text: str,
        icon: str,
        command: Callable,
        is_active: bool = False,
    ):
        super().__init__(master, fg_color="transparent", height=40, cursor="hand2")
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._command = command
        self._text = text
        self._is_active = False

        self.columnconfigure(0, minsize=4)   # Active indicator width
        self.columnconfigure(1, minsize=40)  # Icon width
        self.columnconfigure(2, weight=1)    # Text width
        self.rowconfigure(0, weight=1)

        # Active indicator bar (left edge)
        self._indicator = ctk.CTkFrame(
            self, width=3, fg_color="transparent", corner_radius=2
        )
        self._indicator.grid(row=0, column=0, sticky="ns", pady=8)

        # Icon label
        self._icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI Emoji", 14),
            text_color=Colors.TEXT_SECONDARY,
            anchor="center",
        )
        self._icon_label.grid(row=0, column=1, sticky="nsew")

        # Text label
        self._text_label = ctk.CTkLabel(
            self,
            text=text,
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        )
        self._text_label.grid(row=0, column=2, sticky="nsew", padx=(0, 10))

        # Bind click events to all children
        for widget in [self, self._icon_label, self._text_label, self._indicator]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

        if is_active:
            self.set_active(True)

    def _on_click(self, event=None):
        self._command()

    def _on_enter(self, event=None):
        if not self._is_active:
            self.configure(fg_color=Colors.SIDEBAR_HOVER)

    def _on_leave(self, event=None):
        if not self._is_active:
            self.configure(fg_color="transparent")

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=Colors.SIDEBAR_ACTIVE)
            self._indicator.configure(fg_color=Colors.SIDEBAR_INDICATOR)
            self._icon_label.configure(text_color=Colors.ACCENT)
            self._text_label.configure(text_color=Colors.TEXT_WHITE)
        else:
            self.configure(fg_color="transparent")
            self._indicator.configure(fg_color="transparent")
            self._icon_label.configure(text_color=Colors.TEXT_SECONDARY)
            self._text_label.configure(text_color=Colors.TEXT_SECONDARY)


class Sidebar(ctk.CTkFrame):
    """Left-side navigation panel with stacked menu items."""

    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(
            master,
            width=Spacing.SIDEBAR_WIDTH,
            fg_color=Colors.SIDEBAR_BG,
            corner_radius=0,
        )
        self.pack_propagate(False)

        self._on_navigate = on_navigate
        self._items: dict[str, SidebarItem] = {}

        # App title
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=56)
        title_frame.pack(fill="x", pady=(Spacing.MD, Spacing.XS))
        title_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_frame,
            text="IDM Tool",
            font=Fonts.TITLE,
            text_color=Colors.TEXT_WHITE,
        )
        title_label.pack(side="left", padx=Spacing.LG)

        # Separator
        sep = ctk.CTkFrame(self, height=1, fg_color=Colors.BORDER)
        sep.pack(fill="x", padx=Spacing.MD, pady=Spacing.XS)

        # Sidebar Menu Items (Scrollable to prevent cutoff)
        menu_items = [
            ("Dashboard", "dashboard", "📊"),
            ("Configure (Legacy)", "configure", "🔑"),
            ("Preserve Evaluation", "preserve", "❄️"),
            ("Reset IDM", "reset", "🔄"),
            ("Quick Configure", "quick_act", "⚡"),
            ("Preserve Configuration", "freeze_act", "🛡️"),
            ("Enable Updates", "enable_upd", "🔓"),
            ("Restart IDM", "restart_idm", "🔄"),
            ("Backup & Restore", "backup", "💾"),
        ]

        menu_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", 
            scrollbar_button_color=Colors.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=Colors.SCROLLBAR_HOVER,
        )
        menu_container.pack(fill="both", expand=True, padx=0, pady=0)

        for label, key, icon in menu_items:
            item = SidebarItem(
                menu_container,
                text=label,
                icon=icon,
                command=lambda k=key: self._navigate(k),
                is_active=(key == "dashboard"),
            )
            item.pack(fill="x", padx=Spacing.XS, pady=1)
            self._items[key] = item

        # Bottom separator + settings/logs
        sep2 = ctk.CTkFrame(self, height=1, fg_color=Colors.BORDER)
        sep2.pack(fill="x", padx=Spacing.MD, pady=Spacing.XS)

        bottom_items = [
            ("settings", "⚙️", "Settings"),
            ("logs",     "📋", "Logs"),
            ("about",    "ℹ️", "About"),
        ]

        for key, icon, label in bottom_items:
            item = SidebarItem(
                self,
                text=label,
                icon=icon,
                command=lambda k=key: self._navigate(k),
            )
            item.pack(fill="x", padx=Spacing.XS, pady=1)
            self._items[key] = item

    def _navigate(self, key: str):
        """Handle navigation: update active states and notify parent."""
        for name, item in self._items.items():
            item.set_active(name == key)
        self._on_navigate(key)

    def set_active(self, key: str):
        """Programmatically set the active sidebar item."""
        self._navigate(key)
