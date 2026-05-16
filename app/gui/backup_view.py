"""
Backup & Restore view.

Shows backup list, create/restore/delete actions.
"""

import threading
import customtkinter as ctk
from typing import List

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.backup import list_backups, create_backup, restore_backup, delete_backup, BackupInfo


class BackupView(ctk.CTkFrame):
    """Backup and restore management page."""

    def __init__(self, master, toast_callback):
        super().__init__(master, fg_color="transparent")
        self._toast = toast_callback

        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=Colors.SCROLLBAR_HOVER,
        )
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Title
        title = ctk.CTkLabel(
            container, text="Backup & Restore",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title.pack(fill="x", pady=(0, Spacing.SM))

        desc = ctk.CTkLabel(
            container,
            text="Backup your IDM registry settings before making changes. Restore from any previous backup.",
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, anchor="w",
            wraplength=700,
        )
        desc.pack(fill="x", pady=(0, Spacing.LG))

        # Create backup button
        self._create_btn = ctk.CTkButton(
            container,
            text="  💾  Create New Backup",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            text_color=Colors.TEXT_WHITE,
            height=42,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=self._create_backup,
        )
        self._create_btn.pack(fill="x", pady=(0, Spacing.XL))

        # Backups list header
        list_header = ctk.CTkLabel(
            container, text="Existing Backups",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w",
        )
        list_header.pack(fill="x", pady=(0, Spacing.MD))

        # Backups list frame
        self._list_frame = ctk.CTkFrame(
            container,
            fg_color=Colors.BG_TERTIARY,
            corner_radius=Spacing.CARD_RADIUS,
            border_width=1,
            border_color=Colors.BORDER,
        )
        self._list_frame.pack(fill="x")

        self._refresh_list()

    def _refresh_list(self):
        """Reload the backup list."""
        # Clear existing items
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        backups = list_backups()

        if not backups:
            empty = ctk.CTkLabel(
                self._list_frame,
                text="No backups found. Create one before making changes.",
                font=Fonts.SMALL, text_color=Colors.TEXT_DISABLED,
            )
            empty.pack(padx=Spacing.CARD_PADDING, pady=Spacing.XL)
            return

        for i, backup in enumerate(backups):
            row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
            row.pack(fill="x", padx=Spacing.CARD_PADDING, pady=Spacing.SM)

            # Info
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            name_lbl = ctk.CTkLabel(
                info, text=backup.name,
                font=Fonts.BODY, text_color=Colors.TEXT_PRIMARY, anchor="w",
            )
            name_lbl.pack(fill="x")

            meta_lbl = ctk.CTkLabel(
                info, text=f"📅 {backup.date}  •  📦 {backup.size_kb:.1f} KB",
                font=Fonts.TINY, text_color=Colors.TEXT_DISABLED, anchor="w",
            )
            meta_lbl.pack(fill="x")

            # Restore button
            restore_btn = ctk.CTkButton(
                row, text="Restore", width=80,
                font=Fonts.SMALL,
                fg_color=Colors.BG_ELEVATED,
                hover_color=Colors.ACCENT,
                text_color=Colors.TEXT_PRIMARY,
                height=28,
                corner_radius=Spacing.BUTTON_RADIUS,
                command=lambda b=backup: self._restore(b),
            )
            restore_btn.pack(side="right", padx=(Spacing.SM, 0))

            # Delete button
            del_btn = ctk.CTkButton(
                row, text="Delete", width=70,
                font=Fonts.SMALL,
                fg_color=Colors.BG_ELEVATED,
                hover_color=Colors.ERROR,
                text_color=Colors.TEXT_SECONDARY,
                height=28,
                corner_radius=Spacing.BUTTON_RADIUS,
                command=lambda b=backup: self._delete(b),
            )
            del_btn.pack(side="right")

            # Separator
            if i < len(backups) - 1:
                sep = ctk.CTkFrame(self._list_frame, height=1, fg_color=Colors.BORDER)
                sep.pack(fill="x", padx=Spacing.CARD_PADDING)

    def _create_backup(self):
        """Create a new backup in background."""
        self._create_btn.configure(state="disabled", text="  Creating backup...")

        def _work():
            result = create_backup()
            self.after(0, lambda: self._on_backup_done(result))

        threading.Thread(target=_work, daemon=True).start()

    def _on_backup_done(self, result):
        self._create_btn.configure(state="normal", text="  💾  Create New Backup")
        level = "success" if result.success else "error"
        self._toast(result.message, level)
        self._refresh_list()

    def _restore(self, backup: BackupInfo):
        """Restore from a backup."""
        def _work():
            result = restore_backup(backup.path)
            self.after(0, lambda: self._toast(
                result.message, "success" if result.success else "error"
            ))

        threading.Thread(target=_work, daemon=True).start()

    def _delete(self, backup: BackupInfo):
        """Delete a backup."""
        result = delete_backup(backup.path)
        level = "success" if result.success else "error"
        self._toast(result.message, level)
        self._refresh_list()
