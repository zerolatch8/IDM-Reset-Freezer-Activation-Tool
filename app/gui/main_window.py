"""
Main application window.

Orchestrates sidebar navigation, view switching, status bar,
and toast notifications. This is the top-level GUI entry point.
"""

import customtkinter as ctk

from app.gui.theme import Colors, Fonts, Spacing, Window
from app.gui.sidebar import Sidebar
from app.gui.dashboard import DashboardView
from app.gui.operation_view import OperationView
from app.gui.settings_view import SettingsView
from app.gui.logs_view import LogsView
from app.gui.backup_view import BackupView
from app.gui.about_view import AboutView
from app.gui.components.status_bar import StatusBar
from app.gui.components.toast import ToastManager

from app.backend.engine import activate_idm, freeze_trial, reset_activation, cancel_engine_op
from app.backend.process_manager import OperationState
from app.backend.logger import LogService


class MainWindow(ctk.CTk):
    """Main application window with sidebar navigation and view switching."""

    def __init__(self):
        super().__init__()

        self._logger = LogService.get_instance()
        self._logger.info("GUI application started")

        # ── Window configuration ──────────────────────────
        self.title(Window.TITLE)
        self.geometry(f"{Window.DEFAULT_WIDTH}x{Window.DEFAULT_HEIGHT}")
        self.minsize(Window.MIN_WIDTH, Window.MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_PRIMARY)

        # Dark appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Layout ────────────────────────────────────────
        # Sidebar (left)
        self._sidebar = Sidebar(self, on_navigate=self._navigate)
        self._sidebar.pack(side="left", fill="y")

        # Right container (main content + status bar)
        right = ctk.CTkFrame(self, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        # Status bar (bottom)
        self._status_bar = StatusBar(right)
        self._status_bar.pack(side="bottom", fill="x")

        # Separator above status bar
        sep = ctk.CTkFrame(right, height=1, fg_color=Colors.BORDER)
        sep.pack(side="bottom", fill="x")

        # Main content area
        self._content = ctk.CTkFrame(right, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        self._content.pack(fill="both", expand=True)

        # Toast manager
        self._toast_mgr = ToastManager(self._content)

        # ── View cache ────────────────────────────────────
        self._views = {}
        self._current_view = None

        # Show dashboard by default
        self._navigate("dashboard")

    def _navigate(self, page: str):
        """Switch the main content area to the requested page."""
        # Destroy current view
        if self._current_view:
            self._current_view.pack_forget()
            self._current_view.destroy()
            self._current_view = None

        # Create the requested view
        view = self._create_view(page)
        if view:
            view.pack(fill="both", expand=True)
            self._current_view = view

    def _create_view(self, page: str) -> ctk.CTkFrame:
        """Factory method to create view instances."""
        if page == "dashboard":
            return DashboardView(self._content, navigate_callback=self._sidebar_navigate)

        elif page == "configure":
            return OperationView(
                self._content,
                title="Configure IDM",
                description=(
                    "Configure IDM with a generated registration token. This registers IDM "
                    "by writing Configuration data to the Windows registry."
                ),
                warning=(
                    "Configuration may trigger a invalid token screen in some cases. "
                    "If that happens, use Preserve Evaluation instead."
                ),
                action_label="Configure IDM",
                action_callback=self._run_activate,
                action_color=Colors.ACCENT,
                cancel_callback=cancel_engine_op,
            )

        elif page == "preserve":
            return OperationView(
                self._content,
                title="Preserve Evaluation",
                description=(
                    "preserve the 30-day trial period permanently. This locks IDM's "
                    "trial registry keys so they cannot expire. Recommended method."
                ),
                warning="",
                action_label="Preserve Evaluation Period",
                action_callback=self._run_freeze,
                action_color=Colors.ACCENT,
                cancel_callback=cancel_engine_op,
            )

        elif page == "reset":
            return OperationView(
                self._content,
                title="Reset IDM",
                description=(
                    "Reset all IDM Configuration and trial data. This removes registration tokens, "
                    "trial counters, and CLSID entries to restore IDM to a clean state."
                ),
                warning="This will clear all existing Configuration data. Create a backup first.",
                action_label="Reset Configuration & Trial",
                action_callback=self._run_reset,
                action_color=Colors.ERROR,
                cancel_callback=cancel_engine_op,
            )

        elif page == "quick_act":
            return OperationView(
                self._content,
                title="Quick configure (Direct)",
                description="Apply a generated Token directly to the registry without touching the IDM executables.",
                warning="Does not block IDM servers. IDM may detect the invalid token if online.",
                action_label="Quick configure",
                action_callback=self._run_quick_act,
                action_color=Colors.ACCENT,
            )

        elif page == "freeze_act":
            return OperationView(
                self._content,
                title="preserve Configuration (Recommended)",
                description="The ultimate Configuration method. Applies a Token, blocks validation servers in the Windows hosts file, and disables update checks.",
                warning="You will not be able to update IDM automatically while servers are blocked.",
                action_label="preserve Configuration",
                action_callback=self._run_freeze_act,
                action_color=Colors.ACCENT,
            )

        elif page == "enable_upd":
            return OperationView(
                self._content,
                title="Enable IDM Updates",
                description="Unblocks IDM validation servers from your Windows hosts file so you can update IDM.",
                warning="This WILL break your Configuration! You will need to preserve Configuration again after updating.",
                action_label="Enable Updates",
                action_callback=self._run_enable_upd,
                action_color=Colors.WARNING,
            )

        elif page == "restart_idm":
            return OperationView(
                self._content,
                title="Restart IDM",
                description="Forcefully closes the Internet Download Manager process and relaunches it.",
                warning="",
                action_label="Restart Process",
                action_callback=self._run_restart_idm,
                action_color=Colors.BG_ELEVATED,
            )

        elif page == "backup":
            return BackupView(self._content, toast_callback=self._show_toast)

        elif page == "settings":
            return SettingsView(self._content)

        elif page == "logs":
            return LogsView(self._content)

        elif page == "about":
            return AboutView(self._content)

        return None

    def _sidebar_navigate(self, page: str):
        """Navigate via sidebar (updates active indicator)."""
        self._sidebar.set_active(page)

    # ── Engine operation wrappers ──────────────────────────

    def _run_engine_op(self, engine_func, on_output, on_complete, on_state_change):
        """
        Generic engine operation runner. Thread-safe.
        Called from the worker thread started by OperationView.
        """
        self._logger.info(f"Engine operation starting: {engine_func.__name__}")

        def _on_state(state):
            # Schedule UI update on main thread
            self.after(0, lambda: self._status_bar.set_engine_state(state))
            on_state_change(state)

        def _on_done(result):
            self._logger.info(f"Engine operation done: {result.message}")
            self._show_toast(
                result.message,
                "success" if result.success else "error"
            )
            self.after(0, lambda: on_complete(result))
            
            if result.success and result.state != OperationState.CANCELLED:
                self.after(500, self._prompt_restart)

        result = engine_func(
            on_complete=_on_done,
            on_output=on_output,
            on_state_change=_on_state,
        )
        if result:  # Synchronous failure (pre-flight check failed)
            self._logger.warning(f"Pre-flight check failed: {result.message}")
            on_complete(result)
            self._show_toast(result.message, "error")

    def _run_activate(self, on_output, on_complete, on_state_change):
        """Execute IDM Configuration via the engine."""
        self._run_engine_op(activate_idm, on_output, on_complete, on_state_change)

    def _run_freeze(self, on_output, on_complete, on_state_change):
        """Execute trial preserve via the engine."""
        self._run_engine_op(freeze_trial, on_output, on_complete, on_state_change)

    def _run_reset(self, on_output, on_complete, on_state_change):
        """Execute Configuration reset via the engine."""
        self._run_engine_op(reset_activation, on_output, on_complete, on_state_change)

    # ── Python operation wrappers ──────────────────────────

    def _prompt_restart(self):
        """Show a dialog prompting the user to restart IDM."""
        from app.gui.components.dialog import ConfirmDialog
        
        def _do_restart():
            # Navigate to the restart view and run it automatically
            self._sidebar.set_active("restart_idm")
            # The view is now active, we can trigger the button
            view = self._views.get("restart_idm")
            if view:
                view._on_btn_click()
                
        ConfirmDialog(
            self,
            title="Restart Required",
            message="Internet Download Manager needs to be restarted for the changes to take effect. Restart now?",
            on_confirm=_do_restart
        )

    def _run_python_op(self, py_func, on_output, on_complete, on_state_change):
        """
        Generic Python operation runner. Thread-safe.
        Called from the worker thread started by OperationView.
        """
        self._logger.info(f"Python operation starting: {py_func.__name__}")

        # Update UI state to running
        self.after(0, lambda: self._status_bar.set_engine_state(OperationState.RUNNING))
        self.after(0, lambda: on_state_change(OperationState.RUNNING))

        # Run the synchronous python function
        result = py_func(on_output)

        # Update UI state to completed
        state = OperationState.COMPLETED if result.success else OperationState.FAILED
        self.after(0, lambda s=state: self._status_bar.set_engine_state(s))
        self.after(0, lambda s=state: on_state_change(s))

        self._logger.info(f"Python operation done: {result.message}")
        self._show_toast(
            result.message,
            "success" if result.success else "error"
        )
        self.after(0, lambda: on_complete(result))
        
        if result.success and py_func.__name__ != "restart_idm":
            self.after(500, self._prompt_restart)

    def _run_quick_act(self, on_output, on_complete, on_state_change):
        from app.backend.quick_act import quick_activate
        self._run_python_op(quick_activate, on_output, on_complete, on_state_change)

    def _run_freeze_act(self, on_output, on_complete, on_state_change):
        from app.backend.quick_act import freeze_activation
        self._run_python_op(freeze_activation, on_output, on_complete, on_state_change)

    def _run_enable_upd(self, on_output, on_complete, on_state_change):
        from app.backend.quick_act import enable_updates
        self._run_python_op(enable_updates, on_output, on_complete, on_state_change)

    def _run_restart_idm(self, on_output, on_complete, on_state_change):
        from app.backend.idm_app import restart_idm
        self._run_python_op(restart_idm, on_output, on_complete, on_state_change)

    def _show_toast(self, message: str, level: str = "info"):
        """Show a toast notification (thread-safe)."""
        try:
            self.after(0, lambda: self._toast_mgr.show(message, level))
        except Exception:
            pass
