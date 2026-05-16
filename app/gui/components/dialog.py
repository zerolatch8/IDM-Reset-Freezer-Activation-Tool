"""
Custom dialog components.
"""

import customtkinter as ctk
from typing import Callable
from app.gui.theme import Colors, Fonts, Spacing

class ConfirmDialog(ctk.CTkToplevel):
    """A custom modal confirmation dialog."""
    
    def __init__(self, master, title: str, message: str, on_confirm: Callable, on_cancel: Callable = None):
        super().__init__(master)
        
        self.title("")
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_SECONDARY)
        
        # Center the dialog relative to the master window
        self.update_idletasks()
        if master.winfo_viewable():
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (400 // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (200 // 2)
            self.geometry(f"+{x}+{y}")
            
        self.transient(master)
        self.grab_set()
        
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        
        # Title
        title_lbl = ctk.CTkLabel(
            self, text=title,
            font=Fonts.TITLE, text_color=Colors.TEXT_WHITE,
            anchor="center"
        )
        title_lbl.pack(fill="x", pady=(Spacing.LG, Spacing.SM))
        
        # Message
        msg_lbl = ctk.CTkLabel(
            self, text=message,
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY,
            anchor="center", wraplength=350
        )
        msg_lbl.pack(fill="x", pady=(0, Spacing.LG))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=Spacing.MD, padx=Spacing.LG)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.BG_ELEVATED,
            hover_color=Colors.SIDEBAR_HOVER,
            command=self._cancel
        )
        cancel_btn.grid(row=0, column=0, padx=(0, Spacing.SM), sticky="ew")
        
        confirm_btn = ctk.CTkButton(
            btn_frame, text="Restart Now",
            font=Fonts.BODY_BOLD,
            fg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT_HOVER,
            command=self._confirm
        )
        confirm_btn.grid(row=0, column=1, padx=(Spacing.SM, 0), sticky="ew")

    def _confirm(self):
        self.grab_release()
        self.destroy()
        self._on_confirm()
        
    def _cancel(self):
        self.grab_release()
        self.destroy()
        if self._on_cancel:
            self._on_cancel()
