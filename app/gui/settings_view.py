"""
Settings view.

Toggle switches for application settings with clean card layout.
"""

import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.config import load_config, save_config


class SettingsView(ctk.CTkFrame):
    """Settings page with toggle switches for each config option."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=Colors.SCROLLBAR_HOVER,
        )
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Title
        title = ctk.CTkLabel(
            container, text="Settings",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title.pack(fill="x", pady=(0, Spacing.LG))

        # Settings card
        card = ctk.CTkFrame(
            container,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )
        card.pack(fill="x")

        config = load_config()

        # Setting rows
        self._switches = {}
        settings = [
            ("auto_backup", "Auto Backup",
             "Automatically create a registry backup before operations."),
            ("logging_enabled", "Enable Logging",
             "Save operation logs to the logs directory."),
        ]

        for i, (key, label, desc) in enumerate(settings):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=Spacing.CARD_PADDING, pady=Spacing.MD)

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            lbl = ctk.CTkLabel(
                text_frame, text=label,
                font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY, anchor="w",
            )
            lbl.pack(fill="x")

            desc_lbl = ctk.CTkLabel(
                text_frame, text=desc,
                font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY, anchor="w",
            )
            desc_lbl.pack(fill="x")

            switch = ctk.CTkSwitch(
                row,
                text="",
                width=48,
                fg_color=Colors.BG_INPUT,
                progress_color=Colors.ACCENT,
                button_color=Colors.TEXT_PRIMARY,
                button_hover_color=Colors.TEXT_WHITE,
                command=lambda k=key: self._on_toggle(k),
            )
            switch.pack(side="right", padx=(Spacing.MD, 0))

            if config.get(key, False):
                switch.select()
            else:
                switch.deselect()

            self._switches[key] = switch

            # Separator (except last)
            if i < len(settings) - 1:
                sep = ctk.CTkFrame(card, height=1, fg_color=Colors.BORDER)
                sep.pack(fill="x", padx=Spacing.CARD_PADDING)

    def _on_toggle(self, key: str):
        """Save toggle change to config."""
        config = load_config()
        switch = self._switches[key]
        config[key] = bool(switch.get())
        save_config(config)
