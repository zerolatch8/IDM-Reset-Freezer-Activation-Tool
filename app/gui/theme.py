"""
Design system / theme constants for the GUI.

Windows 11-inspired dark theme with matte charcoal palette.
All colors, fonts, spacing, and sizes are defined here so
the entire UI can be tuned from one place.
"""


# ─── Color Palette ─────────────────────────────────────────────
class Colors:
    # Backgrounds
    BG_PRIMARY = "#1e1e1e"          # Main window background
    BG_SECONDARY = "#252526"        # Sidebar background
    BG_TERTIARY = "#2d2d30"         # Cards / panels
    BG_ELEVATED = "#333337"         # Hover / elevated surfaces
    BG_INPUT = "#3c3c3c"            # Input fields

    # Borders
    BORDER = "#3e3e42"              # Subtle borders
    BORDER_LIGHT = "#4a4a4f"        # Slightly lighter border
    BORDER_FOCUS = "#0078d4"        # Focused input border

    # Text
    TEXT_PRIMARY = "#cccccc"         # Main text
    TEXT_SECONDARY = "#969696"       # Muted / secondary text
    TEXT_DISABLED = "#5a5a5a"        # Disabled state text
    TEXT_WHITE = "#ffffff"           # High-emphasis text

    # Accent
    ACCENT = "#0078d4"              # Windows blue accent
    ACCENT_HOVER = "#1a8ad4"        # Accent on hover
    ACCENT_PRESSED = "#006cbd"      # Accent when pressed

    # Status colors
    SUCCESS = "#4ec94e"             # Green - success
    WARNING = "#f0ad4e"             # Amber - warning
    ERROR = "#e74856"               # Red - error/danger
    INFO = "#0078d4"                # Blue - info

    # Sidebar
    SIDEBAR_BG = "#1c1c1c"          # Sidebar background
    SIDEBAR_HOVER = "#2a2a2a"       # Sidebar item hover
    SIDEBAR_ACTIVE = "#333337"      # Sidebar active item
    SIDEBAR_INDICATOR = "#0078d4"   # Active indicator bar

    # Scrollbar
    SCROLLBAR_BG = "#1e1e1e"
    SCROLLBAR_THUMB = "#424242"
    SCROLLBAR_HOVER = "#4f4f4f"

    # Toast / notifications
    TOAST_BG = "#333337"
    TOAST_BORDER = "#4a4a4f"


# ─── Typography ────────────────────────────────────────────────
class Fonts:
    FAMILY = "Segoe UI"             # Windows system font
    FAMILY_MONO = "Cascadia Code"   # Monospace for logs
    FAMILY_FALLBACK = "Consolas"    # Fallback monospace

    # Sizes
    SIZE_TITLE = 18
    SIZE_HEADING = 14
    SIZE_BODY = 12
    SIZE_SMALL = 10
    SIZE_TINY = 9

    # Pre-built tuples (family, size, ?weight)
    TITLE = (FAMILY, SIZE_TITLE, "bold")
    HEADING = (FAMILY, SIZE_HEADING, "bold")
    BODY = (FAMILY, SIZE_BODY)
    BODY_BOLD = (FAMILY, SIZE_BODY, "bold")
    SMALL = (FAMILY, SIZE_SMALL)
    TINY = (FAMILY, SIZE_TINY)
    MONO = (FAMILY_MONO, SIZE_SMALL)
    MONO_FALLBACK = (FAMILY_FALLBACK, SIZE_SMALL)


# ─── Spacing ───────────────────────────────────────────────────
class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32

    # Specific use cases
    SIDEBAR_WIDTH = 220
    STATUS_BAR_HEIGHT = 32
    CARD_PADDING = 16
    CARD_RADIUS = 8
    BUTTON_RADIUS = 6
    INPUT_RADIUS = 4


# ─── Window ───────────────────────────────────────────────────
class Window:
    TITLE = "IDM Preserver & Configuration Tool"
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    DEFAULT_WIDTH = 1020
    DEFAULT_HEIGHT = 680
