"""
Logs viewer.

Displays real-time logs and allows browsing historical log files.
"""

import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.logger import LogService, LogEntry


class LogsView(ctk.CTkFrame):
    """Real-time and historical log viewer."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self._logger = LogService.get_instance()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Header row
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, Spacing.MD))

        title = ctk.CTkLabel(
            header, text="Logs",
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title.pack(side="left")

        # Clear button
        clear_btn = ctk.CTkButton(
            header, text="Clear All Logs", width=120,
            font=Fonts.SMALL,
            fg_color=Colors.BG_ELEVATED,
            hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_PRIMARY,
            height=30,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=self._clear_logs,
        )
        clear_btn.pack(side="right")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            header, text="Refresh", width=80,
            font=Fonts.SMALL,
            fg_color=Colors.BG_ELEVATED,
            hover_color=Colors.BORDER_LIGHT,
            text_color=Colors.TEXT_PRIMARY,
            height=30,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=self._load_logs,
        )
        refresh_btn.pack(side="right", padx=(0, Spacing.SM))

        # Log console
        self._log_box = ctk.CTkTextbox(
            container,
            font=Fonts.MONO,
            fg_color=Colors.BG_TERTIARY,
            text_color=Colors.TEXT_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=Spacing.CARD_RADIUS,
            state="disabled",
            wrap="word",
        )
        self._log_box.pack(fill="both", expand=True)

        # Tag colors for log levels
        self._log_box.configure(state="normal")
        self._log_box.tag_config("INFO", foreground=Colors.TEXT_SECONDARY)
        self._log_box.tag_config("WARNING", foreground=Colors.WARNING)
        self._log_box.tag_config("ERROR", foreground=Colors.ERROR)
        self._log_box.tag_config("DEBUG", foreground=Colors.TEXT_DISABLED)
        self._log_box.configure(state="disabled")

        # Subscribe to real-time logs
        self._logger.add_listener(self._on_new_log)

        # Load existing buffer
        self._load_logs()

    def _load_logs(self):
        """Load existing logs from buffer into the textbox."""
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")

        for entry in self._logger.get_buffer():
            self._insert_entry(entry)

        # Also load from most recent file if buffer is empty
        if not self._logger.get_buffer():
            files = self._logger.get_log_files()
            if files:
                lines = self._logger.read_log_file(files[0], tail=200)
                for line in lines:
                    level = "INFO"
                    for lev in ["ERROR", "WARNING", "DEBUG", "INFO"]:
                        if f"[{lev}]" in line:
                            level = lev
                            break
                    self._log_box.insert("end", line + "\n", level)

        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _on_new_log(self, entry: LogEntry):
        """Listener callback for real-time log entries."""
        try:
            self.after(0, lambda: self._insert_entry(entry))
        except Exception:
            pass

    def _insert_entry(self, entry: LogEntry):
        """Insert a formatted log entry into the textbox."""
        self._log_box.configure(state="normal")
        line = f"[{entry.timestamp}] [{entry.level}] {entry.message}\n"
        self._log_box.insert("end", line, entry.level)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_logs(self):
        """Clear all log files and the display."""
        self._logger.clear_logs()
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def destroy(self):
        """Clean up listener on destroy."""
        self._logger.remove_listener(self._on_new_log)
        super().destroy()
