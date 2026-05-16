"""
Status bar component.

Fixed bottom bar showing admin status, engine state, version, and update info.
"""

import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing
from app.backend.config import VERSION
from app.backend.admin import is_admin
from app.backend.process_manager import OperationState


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with segmented info display."""

    def __init__(self, master):
        super().__init__(
            master,
            height=Spacing.STATUS_BAR_HEIGHT,
            fg_color=Colors.BG_SECONDARY,
            corner_radius=0,
        )
        self.pack_propagate(False)

        # Left section: admin status
        self._admin_indicator = ctk.CTkLabel(
            self,
            text="",
            font=Fonts.TINY,
            text_color=Colors.TEXT_SECONDARY,
        )
        self._admin_indicator.pack(side="left", padx=Spacing.MD)

        # Separator
        self._sep1 = ctk.CTkFrame(self, width=1, fg_color=Colors.BORDER)
        self._sep1.pack(side="left", fill="y", pady=6)

        # Engine state
        self._engine_label = ctk.CTkLabel(
            self,
            text="Engine: Ready",
            font=Fonts.TINY,
            text_color=Colors.TEXT_SECONDARY,
        )
        self._engine_label.pack(side="left", padx=Spacing.MD)

        # Right section: version
        self._version_label = ctk.CTkLabel(
            self,
            text=f"v{VERSION}",
            font=Fonts.TINY,
            text_color=Colors.TEXT_DISABLED,
        )
        self._version_label.pack(side="right", padx=Spacing.MD)

        # Separator
        self._sep2 = ctk.CTkFrame(self, width=1, fg_color=Colors.BORDER)
        self._sep2.pack(side="right", fill="y", pady=6)

        # Update status
        self._update_label = ctk.CTkLabel(
            self,
            text="",
            font=Fonts.TINY,
            text_color=Colors.TEXT_SECONDARY,
        )
        self._update_label.pack(side="right", padx=Spacing.MD)

        # Initial refresh
        self.refresh_admin_status()

    def refresh_admin_status(self):
        """Update the admin indicator."""
        if is_admin():
            self._admin_indicator.configure(
                text="● Administrator",
                text_color=Colors.SUCCESS,
            )
        else:
            self._admin_indicator.configure(
                text="○ Standard User",
                text_color=Colors.WARNING,
            )

    def set_engine_state(self, state: OperationState):
        """Update the engine state indicator."""
        state_map = {
            OperationState.IDLE: ("Engine: Ready", Colors.TEXT_SECONDARY),
            OperationState.RUNNING: ("Engine: Running...", Colors.ACCENT),
            OperationState.COMPLETED: ("Engine: Done", Colors.SUCCESS),
            OperationState.FAILED: ("Engine: Error", Colors.ERROR),
            OperationState.CANCELLED: ("Engine: Cancelled", Colors.WARNING),
        }
        text, color = state_map.get(state, ("Engine: Unknown", Colors.TEXT_SECONDARY))
        self._engine_label.configure(text=text, text_color=color)

    def set_update_status(self, text: str, is_available: bool = False):
        """Update the update status display."""
        self._update_label.configure(
            text=text,
            text_color=Colors.ACCENT if is_available else Colors.TEXT_SECONDARY,
        )
