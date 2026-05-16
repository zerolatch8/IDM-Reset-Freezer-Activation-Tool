"""
Dashboard view — the default landing page.

Shows IDM status summary, quick action cards, and system overview.
"""

import threading
import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.status import get_idm_status, IDMStatus
from app.backend.admin import is_admin


class StatusCard(ctk.CTkFrame):
    """A small card displaying a key-value status pair."""

    def __init__(self, master, title: str, value: str, color: str = Colors.TEXT_PRIMARY):
        super().__init__(
            master,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )

        title_lbl = ctk.CTkLabel(
            self, text=title, font=Fonts.SMALL,
            text_color=Colors.TEXT_SECONDARY, anchor="w",
        )
        title_lbl.pack(fill="x", padx=Spacing.CARD_PADDING, pady=(Spacing.MD, 2))

        self._value_lbl = ctk.CTkLabel(
            self, text=value, font=Fonts.HEADING,
            text_color=color, anchor="w",
        )
        self._value_lbl.pack(fill="x", padx=Spacing.CARD_PADDING, pady=(0, Spacing.MD))

    def set_value(self, value: str, color: str = None):
        self._value_lbl.configure(text=value)
        if color:
            self._value_lbl.configure(text_color=color)


class QuickActionButton(ctk.CTkButton):
    """A styled action button for the dashboard."""

    def __init__(self, master, text: str, icon: str, command, color: str = Colors.ACCENT):
        super().__init__(
            master,
            text=f"  {icon}  {text}",
            font=Fonts.BODY_BOLD,
            fg_color=color,
            hover_color=Colors.ACCENT_HOVER,
            text_color=Colors.TEXT_WHITE,
            height=42,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=command,
            anchor="w",
        )


class DashboardView(ctk.CTkFrame):
    """Main dashboard view with status cards and quick actions."""

    def __init__(self, master, navigate_callback):
        super().__init__(master, fg_color="transparent")
        self._navigate = navigate_callback

        # Scrollable container
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=Colors.SCROLLBAR_HOVER,
        )
        self._scroll.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Page title
        title = ctk.CTkLabel(
            self._scroll, text="Dashboard",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title.pack(fill="x", pady=(0, Spacing.LG))

        # ── Status Cards Row ──────────────────────────────
        cards_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, Spacing.XL))
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self._card_install = StatusCard(cards_frame, "IDM Status", "Checking...")
        self._card_install.grid(row=0, column=0, padx=(0, Spacing.SM), sticky="nsew")

        self._card_version = StatusCard(cards_frame, "IDM Version", "—")
        self._card_version.grid(row=0, column=1, padx=Spacing.SM, sticky="nsew")

        self._card_activation = StatusCard(cards_frame, "Configuration", "—")
        self._card_activation.grid(row=0, column=2, padx=Spacing.SM, sticky="nsew")

        self._card_admin = StatusCard(cards_frame, "Privileges", "Checking...")
        self._card_admin.grid(row=0, column=3, padx=(Spacing.SM, 0), sticky="nsew")

        # ── Quick Actions ──────────────────────────────────
        actions_title = ctk.CTkLabel(
            self._scroll, text="Quick Actions",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w",
        )
        actions_title.pack(fill="x", pady=(0, Spacing.MD))

        actions_frame = ctk.CTkFrame(
            self._scroll,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )
        actions_frame.pack(fill="x", pady=(0, Spacing.XL))

        actions_inner = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_inner.pack(fill="x", padx=Spacing.CARD_PADDING, pady=Spacing.CARD_PADDING)
        actions_inner.columnconfigure((0, 1, 2), weight=1, uniform="action")

        QuickActionButton(
            actions_inner, "Preserve Evaluation", "❄️",
            lambda: self._navigate("preserve"), Colors.BG_ELEVATED,
        ).grid(row=0, column=0, padx=(0, Spacing.SM), sticky="ew")

        QuickActionButton(
            actions_inner, "Configure IDM", "🔑",
            lambda: self._navigate("configure"), Colors.BG_ELEVATED,
        ).grid(row=0, column=1, padx=Spacing.SM, sticky="ew")

        QuickActionButton(
            actions_inner, "Check Status", "📊",
            self._refresh_status, Colors.BG_ELEVATED,
        ).grid(row=0, column=2, padx=(Spacing.SM, 0), sticky="ew")

        # ── System Info ────────────────────────────────────
        info_title = ctk.CTkLabel(
            self._scroll, text="System Information",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w",
        )
        info_title.pack(fill="x", pady=(0, Spacing.MD))

        self._info_frame = ctk.CTkFrame(
            self._scroll,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )
        self._info_frame.pack(fill="x")

        self._info_text = ctk.CTkLabel(
            self._info_frame,
            text="Loading system information...",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left",
        )
        self._info_text.pack(fill="x", padx=Spacing.CARD_PADDING, pady=Spacing.CARD_PADDING)

        # Load data on a background thread
        self._refresh_status()

    def _refresh_status(self):
        """Refresh all dashboard data in background."""
        # Update admin card immediately (no I/O)
        if is_admin():
            self._card_admin.set_value("Administrator", Colors.SUCCESS)
        else:
            self._card_admin.set_value("Standard User", Colors.WARNING)

        # IDM status in background thread
        self._card_install.set_value("Checking...", Colors.TEXT_SECONDARY)
        threading.Thread(target=self._load_idm_status, daemon=True).start()

    def _load_idm_status(self):
        """Background: query IDM status and update cards on main thread."""
        status = get_idm_status()
        # Schedule UI update on main thread
        self.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status: IDMStatus):
        """Apply IDM status to dashboard cards (must run on main thread)."""
        if not status.installed:
            self._card_install.set_value("Not Installed", Colors.ERROR)
            self._card_version.set_value("—", Colors.TEXT_DISABLED)
            self._card_activation.set_value("—", Colors.TEXT_DISABLED)
            self._info_text.configure(text="IDM is not installed on this system.\nDownload from: internetdownloadmanager.com")
            return

        self._card_install.set_value("Installed", Colors.SUCCESS)
        self._card_version.set_value(status.version or "Unknown", Colors.TEXT_PRIMARY)

        if status.is_registered:
            self._card_activation.set_value("Registered", Colors.SUCCESS)
        elif status.is_trial:
            self._card_activation.set_value("Trial Mode", Colors.WARNING)
        else:
            self._card_activation.set_value("Unknown", Colors.TEXT_SECONDARY)

        info_lines = [f"Install Path: {status.install_path or 'Unknown'}"]
        if status.version:
            info_lines.append(f"Version: {status.version}")
        if status.Token:
            info_lines.append(f"Token: {status.Token}")
        if status.trial_data:
            info_lines.append(f"Trial Data: {status.trial_data}")
        info_lines.append(f"Status: {status.status_text}")
        self._info_text.configure(text="\n".join(info_lines))
