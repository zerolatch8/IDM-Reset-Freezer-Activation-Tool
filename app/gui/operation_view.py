"""
Operation view — used for configure, preserve, and Reset pages.

Provides a consistent layout with description, action button,
real-time output log, and progress tracking.
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.process_manager import OperationState
from app.backend.logger import LogService


class OperationView(ctk.CTkFrame):
    """
    Generic operation page. Used for configure, preserve, and Reset views.
    Each instance is configured with different text and action callback.
    """

    def __init__(
        self,
        master,
        title: str,
        description: str,
        warning: str,
        action_label: str,
        action_callback: Callable,
        action_color: str = Colors.ACCENT,
        cancel_callback: Optional[Callable] = None,
    ):
        super().__init__(master, fg_color="transparent")

        self._action_callback = action_callback
        self._cancel_callback = cancel_callback
        self._action_label = action_label
        self._action_color = action_color
        self._logger = LogService.get_instance()
        self._is_running = False

        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=Colors.SCROLLBAR_THUMB,
            scrollbar_button_hover_color=Colors.SCROLLBAR_HOVER,
        )
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # Title
        title_lbl = ctk.CTkLabel(
            container, text=title,
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE, anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, Spacing.SM))

        # Description
        desc_lbl = ctk.CTkLabel(
            container, text=description,
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY,
            anchor="w", justify="left", wraplength=700,
        )
        desc_lbl.pack(fill="x", pady=(0, Spacing.MD))

        # Warning card
        if warning:
            warn_frame = ctk.CTkFrame(
                container, fg_color="#3d2e1e",
                corner_radius=Spacing.CARD_RADIUS,
                border_width=1, border_color="#6b5a3e",
            )
            warn_frame.pack(fill="x", pady=(0, Spacing.LG))

            warn_lbl = ctk.CTkLabel(
                warn_frame, text=f"⚠  {warning}",
                font=Fonts.SMALL, text_color=Colors.WARNING,
                anchor="w", justify="left", wraplength=650,
            )
            warn_lbl.pack(fill="x", padx=Spacing.CARD_PADDING, pady=Spacing.MD)

        # Action button
        self._action_btn = ctk.CTkButton(
            container,
            text=f"  {action_label}",
            font=Fonts.BODY_BOLD,
            fg_color=action_color,
            hover_color=Colors.ACCENT_HOVER,
            text_color=Colors.TEXT_WHITE,
            height=44,
            corner_radius=Spacing.BUTTON_RADIUS,
            command=self._on_btn_click,
        )
        self._action_btn.pack(fill="x", pady=(0, Spacing.SM))

        # Progress bar (always visible, starts at 0)
        self._progress = ctk.CTkProgressBar(
            container,
            fg_color=Colors.BG_INPUT,
            progress_color=Colors.ACCENT,
            height=4,
            corner_radius=2,
        )
        self._progress.pack(fill="x", pady=(0, Spacing.LG))
        self._progress.set(0)

        # Output console
        output_title = ctk.CTkLabel(
            container, text="Output",
            font=Fonts.HEADING, text_color=Colors.TEXT_PRIMARY, anchor="w",
        )
        output_title.pack(fill="x", pady=(0, Spacing.SM))

        self._output_box = ctk.CTkTextbox(
            container,
            font=Fonts.MONO,
            fg_color=Colors.BG_TERTIARY,
            text_color=Colors.TEXT_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=Spacing.CARD_RADIUS,
            height=250,
            state="disabled",
            wrap="word",
        )
        self._output_box.pack(fill="both", expand=True)

    def _on_btn_click(self):
        """Toggle between starting and cancelling the operation."""
        if self._is_running:
            if self._cancel_callback:
                self.append_output("\n[INFO] Cancelling operation...\n")
                self._cancel_callback()
        else:
            self._start_operation()

    def _start_operation(self):
        """Start the operation in a background thread."""
        self._set_running(True)
        self.clear_output()
        self.append_output("Starting operation...\n")

        def _worker():
            try:
                self._logger.info("Operation thread started")
                self._action_callback(
                    on_output=self._on_output_line,
                    on_complete=self._on_complete,
                    on_state_change=self._on_state_change,
                )
            except Exception as e:
                self._logger.error(f"Operation thread crashed: {e}")
                # Report the crash back to the UI
                self.after(0, lambda: self.append_output(f"\n[FAILED] Error: {e}\n"))
                self.after(0, lambda: self._set_running(False))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _on_output_line(self, line: str):
        """Called from worker thread — schedule on main thread."""
        try:
            self.after(0, lambda l=line: self.append_output(l + "\n"))
        except Exception:
            pass

    def _on_complete(self, result):
        """Called from worker thread — schedule on main thread."""
        from app.backend.process_manager import OperationState
        
        def _update():
            try:
                if result.state == OperationState.CANCELLED:
                    self.append_output(f"\n{'='*50}\n")
                    self.append_output("  [CANCELLED] Operation was aborted by user.\n")
                    self.append_output(f"{'='*50}\n")
                    self._progress.set(0)
                elif result.success:
                    self.append_output(f"\n{'='*50}\n")
                    self.append_output(f"  [SUCCESS] {result.message}\n")
                    self.append_output(f"{'='*50}\n")
                    self._progress.set(1.0)
                else:
                    self.append_output(f"\n{'='*50}\n")
                    self.append_output(f"  [FAILED] {result.message}\n")
                    if result.error:
                        self.append_output(f"  Details: {result.error}\n")
                    self.append_output(f"{'='*50}\n")
                    self._progress.set(0)
                
                self._set_running(False)
            except Exception as e:
                self._logger.error(f"UI update error: {e}")
        self.after(0, _update)

    def _on_state_change(self, state: OperationState):
        """Called from worker thread — schedule on main thread."""
        def _update():
            try:
                if state == OperationState.RUNNING:
                    self._progress.start()
                else:
                    self._progress.stop()
                    if state == OperationState.COMPLETED:
                        self._progress.set(1.0)
                    else:
                        self._progress.set(0)
            except Exception as e:
                self._logger.error(f"Progress bar error: {e}")
        self.after(0, _update)

    def _set_running(self, running: bool):
        """Toggle button state. Must be called from main thread."""
        self._is_running = running
        if running:
            if self._cancel_callback:
                self._action_btn.configure(
                    text="  🛑  Cancel Operation",
                    fg_color=Colors.ERROR,
                    hover_color="#d63f4e",  # Lighter red
                    state="normal",
                )
            else:
                self._action_btn.configure(
                    state="disabled",
                    text="  ⏳  Operation in progress...",
                )
        else:
            self._action_btn.configure(
                state="normal",
                text=f"  {self._action_label}",
                fg_color=self._action_color,
                hover_color=Colors.ACCENT_HOVER,
            )

    def clear_output(self):
        """Clear the output console."""
        self._output_box.configure(state="normal")
        self._output_box.delete("1.0", "end")
        self._output_box.configure(state="disabled")

    def append_output(self, text: str):
        """Append text to the output console and scroll to bottom."""
        self._output_box.configure(state="normal")
        self._output_box.insert("end", text)
        self._output_box.see("end")
        self._output_box.configure(state="disabled")
