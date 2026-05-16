"""
IDM Preserver & Configuration Tool — Main Entry Point

Launches the GUI application with proper admin checks
and error handling.
"""

import sys
import os

# Ensure the project root is on the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Application entry point."""
    from app.backend.config import ensure_directories
    from app.backend.admin import is_admin, request_admin_elevation
    from app.backend.logger import LogService

    # Ensure required directories exist
    ensure_directories()

    # Initialize logger
    logger = LogService.get_instance()

    # Check admin privileges on startup
    if not is_admin():
        logger.warning("Application started without admin privileges")
        success, message = request_admin_elevation()
        if success:
            # Elevated process is starting, exit this one
            sys.exit(0)
        else:
            # Continue without admin — some operations will fail
            logger.warning(f"Continuing without admin: {message}")

    logger.info("Application starting")

    # Launch GUI
    from app.gui.main_window import MainWindow

    app = MainWindow()
    app.mainloop()

    logger.info("Application closed normally")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        # Crash logging
        try:
            from app.backend.logger import LogService
            LogService.get_instance().error(f"Fatal error: {e}")
        except Exception:
            pass

        # Write crash log to file as fallback
        import traceback
        crash_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "idm_tool_crash.log"
        )
        with open(crash_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Crash at {__import__('datetime').datetime.now()}\n")
            traceback.print_exc(file=f)

        print(f"\nFatal error: {e}")
        print(f"Crash log saved to: {crash_file}")
        input("Press Enter to exit...")
        sys.exit(1)
