import subprocess
import os
import sys
import time
import webbrowser
import json
import ctypes
import locale
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)

VERSION = "1.0.0"

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "config.json"
LOG_DIR = Path(__file__).parent / "logs"
BACKUP_DIR = Path(__file__).parent / "IDM_Backup"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

def load_config():
    """Load configuration from file or create default."""
    default_config = {
        "language": "en",
        "auto_backup": True,
        "logging_enabled": True,
        "check_updates_on_start": False,
        "last_update_check": None
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                return {**default_config, **config}
        except Exception as e:
            log_message(f"Error loading config: {e}", "ERROR")
            return default_config
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        log_message(f"Error saving config: {e}", "ERROR")

def log_message(message, level="INFO"):
    """Log messages to file with timestamp."""
    config = load_config()
    if not config.get("logging_enabled", True):
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"idm_manager_{datetime.now().strftime('%Y%m%d')}.log"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception as e:
        print(Fore.RED + f"Failed to write log: {e}")

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """Request administrator privileges."""
    if not is_admin():
        print(Fore.YELLOW + "\n⚠️  Administrator privileges required for this operation.")
        choice = input(Fore.YELLOW + "Restart as administrator? (yes/no): ").lower()
        
        if choice in ['yes', 'y']:
            print(Fore.YELLOW + "Attempting to restart with admin privileges...")
            log_message("Requesting admin privileges", "INFO")
            try:
                # Build command line arguments
                import subprocess
                script_path = os.path.abspath(__file__)
                
                # Use ShellExecute to request elevation
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, f'"{script_path}"', None, 1
                )
                
                # If successful (result > 32), exit current process
                if result > 32:
                    sys.exit(0)
                else:
                    print(Fore.RED + "\n❌ Failed to elevate privileges (UAC cancelled or error).")
                    log_message("Admin elevation cancelled or failed", "WARNING")
                    return False
                    
            except Exception as e:
                log_message(f"Failed to elevate privileges: {e}", "ERROR")
                print(Fore.RED + f"\n❌ Failed to elevate privileges: {e}")
                return False
        else:
            print(Fore.YELLOW + "\n⚠️  Continuing without admin privileges (some operations may fail)...")
            log_message("User declined admin privileges", "INFO")
            return False
    return True

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print(Fore.CYAN + "=" * 70)
    print(Fore.CYAN + "=" + Fore.WHITE + Back.BLUE + " IDM Preserver & Configuration Tool ".center(68) + Fore.CYAN + "=")
    print(Fore.CYAN + "=" + Fore.YELLOW + f" Version {VERSION} ".center(68) + Fore.CYAN + "=")
    print(Fore.CYAN + "=" * 70)
    print(Fore.MAGENTA + """
     ██╗██████╗ ███╗   ███╗    ███████╗██████╗ ███████╗███████╗███████╗███████╗██████╗
     ██║██╔══██╗████╗ ████║    ██╔════╝██╔══██╗██╔════╝██╔════╝╚══███╔╝██╔════╝██╔══██╗
     ██║██║  ██║██╔████╔██║    █████╗  ██████╔╝█████╗  █████╗    ███╔╝ █████╗  ██████╔╝
     ██║██║  ██║██║╚██╔╝██║    ██╔══╝  ██╔══██╗██╔══╝  ██╔══╝   ███╔╝  ██╔══╝  ██╔══██╗
     ██║██████╔╝██║ ╚═╝ ██║    ██║     ██║  ██║███████╗███████╗███████╗███████╗██║  ██║
     ╚═╝╚═════╝ ╚═╝     ╚═╝    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
                                                            BY ZEROLATCH (CREDITS: ZIEDEV)
    """)
    print(Fore.CYAN + "=" * 70)

def print_menu():
    """Print the main menu options."""
    print(Fore.GREEN + "\nMAIN MENU:")
    print(Fore.WHITE + "=" * 70)
    print(Fore.YELLOW + " [1]" + Fore.WHITE + " Configure IDM")
    print(Fore.YELLOW + " [2]" + Fore.WHITE + " Preserve Evaluation (Recommended)")
    print(Fore.YELLOW + " [3]" + Fore.WHITE + " Reset Configuration/Trial")
    print(Fore.YELLOW + " [4]" + Fore.WHITE + " Check IDM Status")
    print(Fore.YELLOW + " [5]" + Fore.WHITE + " Backup/Restore IDM Settings")
    print(Fore.WHITE + "=" * 70)
    print(Fore.YELLOW + " [6]" + Fore.WHITE + " Download IDM")
    print(Fore.YELLOW + " [7]" + Fore.WHITE + " Visit GitHub Repository")
    print(Fore.YELLOW + " [8]" + Fore.WHITE + " Settings")
    print(Fore.YELLOW + " [0]" + Fore.WHITE + " Exit")
    print(Fore.WHITE + "=" * 70)

def show_progress(message, duration=3):
    """Show a progress bar with the given message."""
    print(Fore.CYAN + f"\n{message}")
    print(Fore.YELLOW + "Progress: ", end="")
    for i in range(50):
        time.sleep(duration/50)
        print(Fore.GREEN + "█", end="", flush=True)
    print(Fore.GREEN + " Done!")

def check_network_connectivity():
    """Check if network is available."""
    try:
        # Try to ping GitHub
        result = subprocess.run(
            ["ping", "-n", "1", "github.com"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        log_message(f"Network check failed: {e}", "WARNING")
        return False

def run_batch_file(parameter="", show_output=True):
    """Run the zerolatch.cmd batch file with optional parameters."""
    batch_file = Path(__file__).parent / "zerolatch.cmd"
    
    if not batch_file.exists():
        print(Fore.RED + f"\n❌ Error: Batch file not found at {batch_file}")
        log_message(f"Batch file not found: {batch_file}", "ERROR")
        input(Fore.YELLOW + "\nPress Enter to return to the main menu...")
        return False
    
    # Check admin privileges - warn but allow to continue
    if not is_admin():
        print(Fore.YELLOW + "\n⚠️  This operation works best with administrator privileges.")
        choice = input(Fore.YELLOW + "Continue anyway? (yes/no): ").lower()
        
        if choice not in ['yes', 'y']:
            print(Fore.CYAN + "\nTip: Right-click the script and select 'Run as administrator'")
            input(Fore.YELLOW + "\nPress Enter to return to the main menu...")
            return False
        else:
            print(Fore.YELLOW + "\n⚠️  Continuing without admin (operation may fail)...")
    
    # Check network for online operations
    if parameter in ["/act", "/frz"]:
        print(Fore.CYAN + "\n🌐 Checking network connectivity...")
        if not check_network_connectivity():
            print(Fore.RED + "❌ Network connectivity issue detected!")
            print(Fore.YELLOW + "Please check your internet connection and try again.")
            log_message("Network connectivity check failed", "WARNING")
            input(Fore.YELLOW + "\nPress Enter to return to the main menu...")
            return False
        print(Fore.GREEN + "✓ Network connection OK")
    
    try:
        if parameter:
            show_progress(f"Running command with parameter: {parameter}")
            log_message(f"Executing: zerolatch.cmd {parameter}", "INFO")
            
            # Use PowerShell to run the batch file with better encoding support
            cmd = f'cmd.exe /c "chcp 65001 >nul && \"{batch_file}\" {parameter}"'
            
            if show_output:
                process = subprocess.run(
                    cmd,
                    shell=True,
                    check=False,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                process = subprocess.run(
                    cmd,
                    shell=True,
                    check=False,
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace'
                )
        else:
            show_progress("Launching IDM Configuration Script")
            log_message("Executing: zerolatch.cmd", "INFO")
            cmd = f'cmd.exe /c "chcp 65001 >nul && \"{batch_file}\""'
            process = subprocess.run(cmd, shell=True, check=False)

        if process.returncode == 0:
            print(Fore.GREEN + "\n✓ Operation completed successfully!")
            log_message("Batch operation completed successfully", "INFO")
            return True
        else:
            print(Fore.YELLOW + f"\n⚠️  Operation completed with warnings (exit code: {process.returncode})")
            log_message(f"Batch operation completed with code: {process.returncode}", "WARNING")
            return True
            
    except subprocess.TimeoutExpired:
        print(Fore.RED + "\n❌ Operation timed out. Please try again.")
        log_message("Batch operation timed out", "ERROR")
        return False
    except Exception as e:
        print(Fore.RED + f"\n❌ An error occurred: {e}")
        log_message(f"Batch execution error: {e}", "ERROR")
        if "introuvable" in str(e) or "not found" in str(e).lower():
            print(Fore.YELLOW + "\nTip: Make sure zerolatch.cmd is in the same folder as this script.")
        return False
    finally:
        input(Fore.YELLOW + "\nPress Enter to return to the main menu...")

def check_idm_status():
    """Check the current status of IDM installation."""
    print(Fore.CYAN + "\n🔍 Checking IDM status...")
    log_message("Checking IDM status", "INFO")

    # Check if IDM is installed
    idm_paths = [
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Internet Download Manager', 'IDMan.exe'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Internet Download Manager', 'IDMan.exe')
    ]

    idm_installed = None
    for path in idm_paths:
        if os.path.exists(path):
            idm_installed = path
            break

    if not idm_installed:
        print(Fore.RED + "❌ IDM is not installed on this system.")
        log_message("IDM not found", "INFO")
        input(Fore.YELLOW + "\nPress Enter to return to the main menu...")
        return

    print(Fore.GREEN + f"✓ IDM found at: {idm_installed}")

    # Run a command to check IDM status with better encoding
    try:
        # Create a temporary batch file to check IDM status
        temp_batch = Path(__file__).parent / "check_idm_temp.bat"
        
        with open(temp_batch, "w", encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('chcp 65001 >nul\n')
            f.write('setlocal\n')
            f.write('for /f "tokens=2*" %%a in (\'reg query "HKCU\\Software\\DownloadManager" /v Serial 2^>nul\') do set "Token=%%b"\n')
            f.write('for /f "tokens=2*" %%a in (\'reg query "HKCU\\Software\\DownloadManager" /v tvfrdt 2^>nul\') do set "trial=%%b"\n')
            f.write('for /f "tokens=2*" %%a in (\'reg query "HKCU\\Software\\DownloadManager" /v idmvers 2^>nul\') do set "version=%%b"\n')
            f.write('echo IDM_STATUS_BEGIN\n')
            f.write('if defined version echo Version: %version%\n')
            f.write('if defined Token echo Token: %Token%\n')
            f.write('if defined trial echo Trial: %trial%\n')
            f.write('if not defined Token if not defined trial echo Status: Unknown\n')
            f.write('echo IDM_STATUS_END\n')

        # Run the batch file and capture output
        result = subprocess.run(
            ["cmd.exe", "/c", str(temp_batch)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Parse the output
        output = result.stdout
        if "IDM_STATUS_BEGIN" in output:
            status_section = output.split("IDM_STATUS_BEGIN")[1].split("IDM_STATUS_END")[0].strip()
        else:
            status_section = ""

        print(Fore.GREEN + "\n📊 IDM Status:")
        print(Fore.WHITE + "=" * 50)

        if "Version:" in status_section:
            version_line = [line for line in status_section.split('\n') if "Version:" in line][0]
            print(Fore.CYAN + version_line)

        if "Token:" in status_section:
            print(Fore.GREEN + "✓ IDM is registered with a registration token.")
            log_message("IDM is registered", "INFO")
        elif "Trial:" in status_section:
            print(Fore.YELLOW + "⚠️  IDM is in trial mode.")
            log_message("IDM is in trial mode", "INFO")
        else:
            print(Fore.RED + "❌ IDM status could not be determined.")
            log_message("IDM status unknown", "WARNING")

        print(Fore.WHITE + "=" * 50)

        # Clean up
        if temp_batch.exists():
            temp_batch.unlink()

    except Exception as e:
        print(Fore.RED + f"❌ Error checking IDM status: {e}")
        log_message(f"Error checking IDM status: {e}", "ERROR")

    input(Fore.YELLOW + "\nPress Enter to return to the main menu...")

def backup_restore_idm():
    """Backup or restore IDM settings."""
    while True:
        clear_screen()
        print_header()
        print(Fore.GREEN + "\n💾 BACKUP/RESTORE IDM SETTINGS:")
        print(Fore.WHITE + "=" * 70)
        print(Fore.YELLOW + " [1]" + Fore.WHITE + " Backup IDM Settings")
        print(Fore.YELLOW + " [2]" + Fore.WHITE + " Restore IDM Settings")
        print(Fore.YELLOW + " [3]" + Fore.WHITE + " View Existing Backups")
        print(Fore.YELLOW + " [0]" + Fore.WHITE + " Return to Main Menu")
        print(Fore.WHITE + "=" * 70)

        choice = input(Fore.GREEN + "\nEnter your choice: ")

        if choice == "1":
            # Backup IDM settings
            BACKUP_DIR.mkdir(exist_ok=True)

            try:
                show_progress("Backing up IDM settings")
                log_message("Starting IDM backup", "INFO")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = BACKUP_DIR / f"IDM_Settings_{timestamp}.reg"

                # Create a batch file for backup with UTF-8 support
                temp_batch = Path(__file__).parent / "backup_idm_temp.bat"
                
                with open(temp_batch, "w", encoding='utf-8') as f:
                    f.write('@echo off\n')
                    f.write('chcp 65001 >nul\n')
                    f.write(f'reg export "HKCU\\Software\\DownloadManager" "{backup_file}" /y\n')
                    f.write(f'echo Backup saved to: {backup_file}\n')

                # Run the backup
                subprocess.run(["cmd.exe", "/c", str(temp_batch)], check=True)

                # Clean up
                if temp_batch.exists():
                    temp_batch.unlink()

                print(Fore.GREEN + f"\n✓ Backup completed successfully!")
                print(Fore.CYAN + f"📁 Saved to: {backup_file}")
                log_message(f"Backup created: {backup_file}", "INFO")
                
            except Exception as e:
                print(Fore.RED + f"\n❌ Error during backup: {e}")
                log_message(f"Backup error: {e}", "ERROR")

            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "2":
            # Restore IDM settings
            if not BACKUP_DIR.exists():
                print(Fore.RED + "\n❌ No backup directory found!")
                input(Fore.YELLOW + "\nPress Enter to continue...")
                continue

            backup_files = sorted(
                [f for f in BACKUP_DIR.iterdir() if f.name.startswith("IDM_Settings_") and f.suffix == ".reg"],
                reverse=True
            )

            if not backup_files:
                print(Fore.RED + "\n❌ No backup files found!")
                input(Fore.YELLOW + "\nPress Enter to continue...")
                continue

            print(Fore.GREEN + "\n📂 Available backup files:")
            print(Fore.WHITE + "=" * 70)
            for i, file in enumerate(backup_files, 1):
                file_size = file.stat().st_size / 1024  # Size in KB
                file_date = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(Fore.YELLOW + f" [{i}]" + Fore.WHITE + f" {file.name}")
                print(Fore.GRAY + f"     📅 {file_date}  |  📦 {file_size:.1f} KB")

            try:
                file_choice = input(Fore.GREEN + f"\nEnter the number (1-{len(backup_files)}) or 0 to cancel: ")
                
                if file_choice == "0":
                    continue

                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(backup_files):
                    selected_file = backup_files[file_idx]

                    print(Fore.YELLOW + f"\n⚠️  This will restore settings from: {selected_file.name}")
                    confirm = input(Fore.YELLOW + "Are you sure? (yes/no): ").lower()
                    
                    if confirm in ['yes', 'y']:
                        show_progress("Restoring IDM settings")
                        log_message(f"Restoring from: {selected_file}", "INFO")

                        # Import the registry file
                        subprocess.run(["reg", "import", str(selected_file)], check=True)

                        print(Fore.GREEN + "\n✓ Restore completed successfully!")
                        log_message("Restore completed", "INFO")
                    else:
                        print(Fore.YELLOW + "\nRestore cancelled.")
                else:
                    print(Fore.RED + "\n❌ Invalid selection!")
                    
            except ValueError:
                print(Fore.RED + "\n❌ Please enter a valid number!")
            except Exception as e:
                print(Fore.RED + f"\n❌ Error during restore: {e}")
                log_message(f"Restore error: {e}", "ERROR")

            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "3":
            # View existing backups
            if not BACKUP_DIR.exists() or not any(BACKUP_DIR.iterdir()):
                print(Fore.RED + "\n❌ No backups found!")
            else:
                backup_files = sorted(
                    [f for f in BACKUP_DIR.iterdir() if f.suffix == ".reg"],
                    reverse=True
                )
                
                print(Fore.GREEN + f"\n📂 Found {len(backup_files)} backup(s):")
                print(Fore.WHITE + "=" * 70)
                
                total_size = 0
                for i, file in enumerate(backup_files, 1):
                    file_size = file.stat().st_size / 1024
                    total_size += file_size
                    file_date = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    print(Fore.CYAN + f" {i}. {file.name}")
                    print(Fore.GRAY + f"    📅 {file_date}  |  📦 {file_size:.1f} KB")
                
                print(Fore.WHITE + "=" * 70)
                print(Fore.CYAN + f"Total backup size: {total_size:.1f} KB")
                
            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "0":
            break
        else:
            print(Fore.RED + "\n❌ Invalid choice. Please try again.")
            time.sleep(1)

def settings_menu():
    """Display and manage settings."""
    while True:
        clear_screen()
        print_header()
        config = load_config()
        
        print(Fore.GREEN + "\n⚙️  SETTINGS:")
        print(Fore.WHITE + "=" * 70)
        print(Fore.YELLOW + " [1]" + Fore.WHITE + f" Auto Backup: {Fore.GREEN if config['auto_backup'] else Fore.RED}{'Enabled' if config['auto_backup'] else 'Disabled'}")
        print(Fore.YELLOW + " [2]" + Fore.WHITE + f" Logging: {Fore.GREEN if config['logging_enabled'] else Fore.RED}{'Enabled' if config['logging_enabled'] else 'Disabled'}")
        print(Fore.YELLOW + " [3]" + Fore.WHITE + f" Check Updates on Start: {Fore.GREEN if config['check_updates_on_start'] else Fore.RED}{'Enabled' if config['check_updates_on_start'] else 'Disabled'}")
        print(Fore.YELLOW + " [4]" + Fore.WHITE + " View Logs")
        print(Fore.YELLOW + " [5]" + Fore.WHITE + " Clear Logs")
        print(Fore.YELLOW + " [0]" + Fore.WHITE + " Return to Main Menu")
        print(Fore.WHITE + "=" * 70)
        
        choice = input(Fore.GREEN + "\nEnter your choice: ")
        
        if choice == "1":
            config['auto_backup'] = not config['auto_backup']
            save_config(config)
            print(Fore.GREEN + f"\n✓ Auto Backup {'enabled' if config['auto_backup'] else 'disabled'}!")
            time.sleep(1)
        elif choice == "2":
            config['logging_enabled'] = not config['logging_enabled']
            save_config(config)
            print(Fore.GREEN + f"\n✓ Logging {'enabled' if config['logging_enabled'] else 'disabled'}!")
            time.sleep(1)
        elif choice == "3":
            config['check_updates_on_start'] = not config['check_updates_on_start']
            save_config(config)
            print(Fore.GREEN + f"\n✓ Check Updates on Start {'enabled' if config['check_updates_on_start'] else 'disabled'}!")
            time.sleep(1)
        elif choice == "4":
            # View logs
            log_files = sorted(LOG_DIR.glob("*.log"), reverse=True)
            if not log_files:
                print(Fore.YELLOW + "\n📝 No log files found.")
                input(Fore.YELLOW + "Press Enter to continue...")
                continue
                
            print(Fore.GREEN + f"\n📝 Found {len(log_files)} log file(s):")
            for i, log_file in enumerate(log_files, 1):
                print(Fore.CYAN + f" [{i}] {log_file.name}")
            
            try:
                choice = input(Fore.GREEN + f"\nEnter log number to view (1-{len(log_files)}) or 0 to cancel: ")
                if choice != "0":
                    idx = int(choice) - 1
                    if 0 <= idx < len(log_files):
                        with open(log_files[idx], 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            print(Fore.WHITE + "\n" + "=" * 70)
                            print(Fore.CYAN + f"Last 50 lines of {log_files[idx].name}:")
                            print(Fore.WHITE + "=" * 70)
                            for line in lines[-50:]:
                                print(Fore.GRAY + line.rstrip())
            except (ValueError, IndexError):
                print(Fore.RED + "\n❌ Invalid choice!")
            
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == "5":
            # Clear logs
            confirm = input(Fore.YELLOW + "\n⚠️  Clear all logs? (yes/no): ").lower()
            if confirm in ['yes', 'y']:
                for log_file in LOG_DIR.glob("*.log"):
                    log_file.unlink()
                print(Fore.GREEN + "\n✓ Logs cleared!")
                time.sleep(1)
        elif choice == "0":
            break
        else:
            print(Fore.RED + "\n❌ Invalid choice!")
            time.sleep(1)

def main():
    """Main application function."""
    log_message("Application started", "INFO")
    
    # Show admin status on startup
    if not is_admin():
        print(Fore.YELLOW + "\n⚠️  Running without administrator privileges.")
        print(Fore.CYAN + "Some operations may require admin rights. You'll be prompted when needed.\n")
        time.sleep(2)
    else:
        print(Fore.GREEN + "\n✓ Running with administrator privileges.\n")
        time.sleep(1)
    
    # Check for updates on start if enabled
    config = load_config()
    if config.get('check_updates_on_start', False):
        # No updates for final release
        pass
    
    while True:
        print_header()
        print_menu()

        choice = input(Fore.GREEN + "\nEnter your choice: ")

        if choice == "1":
            run_batch_file("/act")
        elif choice == "2":
            run_batch_file("/frz")
        elif choice == "3":
            run_batch_file("/res")
        elif choice == "4":
            check_idm_status()
        elif choice == "5":
            backup_restore_idm()
        elif choice == "6":
            webbrowser.open("https://www.internetdownloadmanager.com/download.html")
            print(Fore.GREEN + "\n✓ Browser opened!")
            log_message("Opened IDM download page", "INFO")
            input(Fore.YELLOW + "Press Enter to continue...")
        elif choice == "7":
            webbrowser.open("https://github.com/zerolatch8/IDM-Reset-Freezer-Activation-Tool")
            print(Fore.GREEN + "\n✓ Browser opened!")
            log_message("Opened GitHub repository", "INFO")
            input(Fore.YELLOW + "Press Enter to continue...")
        elif choice == "8":
            settings_menu()
        elif choice == "0":
            print(Fore.GREEN + "\n👋 Thank you for using IDM Preserver & Configuration Tool!")
            log_message("Application closed normally", "INFO")
            time.sleep(1)
            sys.exit(0)
        else:
            print(Fore.RED + "\n❌ Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n⚠️  Program interrupted by user. Exiting...")
        log_message("Application interrupted by user", "INFO")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n\n❌ An unexpected error occurred: {e}")
        log_message(f"Unexpected error: {e}", "ERROR")
        input(Fore.YELLOW + "\nPress Enter to exit...")
        sys.exit(1)


