"""
About view.

Simple informational page with version, credits, and links.
"""

import webbrowser
import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.config import VERSION
from app.backend.network import GITHUB_REPO_URL, IDM_DOWNLOAD_URL


class AboutView(ctk.CTkFrame):
    """About page with app info, credits, and external links."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Title
        title = ctk.CTkLabel(
            container, text="About",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title.pack(fill="x", pady=(0, Spacing.LG))

        # Info card
        card = ctk.CTkFrame(
            container,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )
        card.pack(fill="x", pady=(0, Spacing.LG))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=Spacing.XL, pady=Spacing.XL)

        app_name = ctk.CTkLabel(
            inner, text="IDM Preserver & Configuration Tool",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        app_name.pack(fill="x", pady=(0, Spacing.XS))

        version_lbl = ctk.CTkLabel(
            inner, text=f"Version {VERSION}",
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor="w",
        )
        version_lbl.pack(fill="x", pady=(0, Spacing.MD))

        author = ctk.CTkLabel(
            inner, text="Developed by ZeroLatch | Credits: ZIEDEV",
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor="w",
        )
        author.pack(fill="x", pady=(0, Spacing.SM))

        license_lbl = ctk.CTkLabel(
            inner, text="Licensed under GNU GPL v3.0",
            font=Fonts.SMALL, text_color=Colors.TEXT_DISABLED, anchor="w",
        )
        license_lbl.pack(fill="x", pady=(0, Spacing.LG))

        # Links
        links_frame = ctk.CTkFrame(inner, fg_color="transparent")
        links_frame.pack(fill="x")

        github_btn = ctk.CTkButton(
            links_frame,
            text="GitHub Repository",
            font=Fonts.BODY,
            fg_color=Colors.BG_ELEVATED,
            hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.ACCENT,
            height=36,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=lambda: webbrowser.open(GITHUB_REPO_URL),
        )
        github_btn.pack(side="left", padx=(0, Spacing.SM))

        download_btn = ctk.CTkButton(
            links_frame,
            text="Download IDM",
            font=Fonts.BODY,
            fg_color=Colors.BG_ELEVATED,
            hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.ACCENT,
            height=36,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=lambda: webbrowser.open(IDM_DOWNLOAD_URL),
        )
        download_btn.pack(side="left")

        # Disclaimer
        disclaimer = ctk.CTkLabel(
            container,
            text="This tool is for educational and research purposes only. "
                 "Use at your own risk. The authors are not responsible for "
                 "any misuse or damage caused by this software.",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_DISABLED,
            anchor="w",
            justify="left",
            wraplength=700,
        )
        disclaimer.pack(fill="x")
