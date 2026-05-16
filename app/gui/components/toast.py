"""
Toast notification component.

Clean inline notifications that appear below content and auto-dismiss.
"""

import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing


class Toast(ctk.CTkFrame):
    """An inline notification bar that auto-dismisses."""

    LEVEL_STYLES = {
        "success": {"bg": "#1a3a1a", "border": "#2d5a2d", "text": "#4ec94e", "icon": ">>"},
        "error":   {"bg": "#3a1a1a", "border": "#5a2d2d", "text": "#e74856", "icon": ">>"},
        "warning": {"bg": "#3a3318", "border": "#5a4d2d", "text": "#f0ad4e", "icon": ">>"},
        "info":    {"bg": "#1a2a3a", "border": "#2d4a5a", "text": "#0078d4", "icon": ">>"},
    }

    def __init__(self, master, message: str, level: str = "info", duration: float = 4.0):
        style = self.LEVEL_STYLES.get(level, self.LEVEL_STYLES["info"])

        super().__init__(
            master,
            fg_color=style["bg"],
            border_width=1,
            border_color=style["border"],
            corner_radius=Spacing.BUTTON_RADIUS,
            height=36,
        )
        self.pack_propagate(False)

        # Icon/prefix
        icon_lbl = ctk.CTkLabel(
            self,
            text=style["icon"],
            font=(Fonts.FAMILY, 11, "bold"),
            text_color=style["text"],
            width=24,
        )
        icon_lbl.pack(side="left", padx=(Spacing.MD, 4))

        # Message
        msg_lbl = ctk.CTkLabel(
            self,
            text=message,
            font=(Fonts.FAMILY, 11),
            text_color=style["text"],
            anchor="w",
        )
        msg_lbl.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))

        # Dismiss button
        close_btn = ctk.CTkLabel(
            self,
            text="x",
            font=(Fonts.FAMILY, 11),
            text_color=style["text"],
            width=20,
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=(0, Spacing.SM))
        close_btn.bind("<Button-1>", lambda e: self._dismiss())

        # Auto-dismiss
        if duration > 0:
            self._dismiss_id = self.after(int(duration * 1000), self._dismiss)

    def _dismiss(self):
        try:
            self.destroy()
        except Exception:
            pass


class ToastManager:
    """Manages toast stacking inside a container."""

    def __init__(self, master):
        self._master = master
        # Container at the top of the content area
        self._container = ctk.CTkFrame(master, fg_color="transparent")
        self._container.place(relx=0.5, rely=0.0, anchor="n", relwidth=0.6, y=Spacing.SM)

    def show(self, message: str, level: str = "info", duration: float = 4.0):
        """Show a toast notification."""
        toast = Toast(self._container, message, level, duration)
        toast.pack(fill="x", pady=(0, 4))
