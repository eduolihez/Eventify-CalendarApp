import tkinter as tk
from tkinter import ttk
import os

class ThemeManager:
    """Manages application themes (light/dark)"""
    
    def __init__(self, root, db_manager):
        """Initialize the theme manager"""
        self.root = root
        self.db_manager = db_manager
        
        # Define iOS-inspired theme colors with refined palette
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "accent": "#FF2D55",  # iOS pink
                "secondary_accent": "#007AFF",  # iOS blue
                "tertiary_accent": "#5AC8FA",  # iOS light blue
                "success": "#34C759",  # iOS green
                "warning": "#FF9500",  # iOS orange
                "danger": "#FF3B30",  # iOS red
                "button": "#f2f2f7",  # iOS light gray
                "button_hover": "#e5e5ea",  # iOS lighter gray for hover
                "highlight": "#e5e5ea",  # iOS lighter gray
                "border": "#d1d1d6",  # iOS light border
                "card": "#ffffff",
                "header": "#f9f9f9",
                "today": "#FF2D55",  # iOS pink for today highlight
                "event_colors": [
                    "#FF2D55",  # Pink
                    "#007AFF",  # Blue
                    "#34C759",  # Green
                    "#FF9500",  # Orange
                    "#5856D6",  # Purple
                    "#FF3B30",  # Red
                    "#5AC8FA",  # Light Blue
                    "#FFCC00"   # Yellow
                ]
            },
            "dark": {
                "bg": "#1c1c1e",
                "fg": "#ffffff",
                "accent": "#FF375F",  # iOS pink (dark mode)
                "secondary_accent": "#0A84FF",  # iOS blue (dark mode)
                "tertiary_accent": "#64D2FF",  # iOS light blue (dark mode)
                "success": "#30D158",  # iOS green (dark mode)
                "warning": "#FF9F0A",  # iOS orange (dark mode)
                "danger": "#FF453A",  # iOS red (dark mode)
                "button": "#2c2c2e",  # iOS dark gray
                "button_hover": "#3a3a3c",  # iOS darker gray for hover
                "highlight": "#3a3a3c",  # iOS darker gray
                "border": "#38383a",  # iOS dark border
                "card": "#2c2c2e",
                "header": "#2c2c2e",
                "today": "#FF375F",  # iOS pink for today highlight
                "event_colors": [
                    "#FF375F",  # Pink
                    "#0A84FF",  # Blue
                    "#30D158",  # Green
                    "#FF9F0A",  # Orange
                    "#BF5AF2",  # Purple
                    "#FF453A",  # Red
                    "#64D2FF",  # Light Blue
                    "#FFD60A"   # Yellow
                ]
            }
        }
        
        # Load the saved theme or use light theme as default
        self.current_theme = self.db_manager.get_setting("theme") or "light"
        
        # Apply the theme
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        if theme_name not in self.themes:
            theme_name = "light"
        
        theme = self.themes[theme_name]
        
        # Configure ttk styles
        style = ttk.Style(self.root)
        
        # Configure common elements
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        
        # iOS-style buttons - more refined with better padding and font
        style.configure("iOS.TButton", 
                        background=theme["secondary_accent"], 
                        foreground="#ffffff", 
                        font=("SF Pro Display", 11, "bold"),
                        borderwidth=0,
                        padding=(12, 8))
        style.map("iOS.TButton",
                 background=[("active", theme["tertiary_accent"]), ("pressed", theme["tertiary_accent"])],
                 foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        # Secondary iOS-style buttons
        style.configure("iOS.Secondary.TButton", 
                        background=theme["button"], 
                        foreground=theme["secondary_accent"], 
                        font=("SF Pro Display", 11, "bold"),
                        borderwidth=1,
                        padding=(12, 8))
        style.map("iOS.Secondary.TButton",
                 background=[("active", theme["button_hover"]), ("pressed", theme["button_hover"])],
                 foreground=[("active", theme["secondary_accent"]), ("pressed", theme["secondary_accent"])])
        
        # Today button
        style.configure("Today.TButton", 
                        background=theme["accent"], 
                        foreground="#ffffff", 
                        font=("SF Pro Display", 11, "bold"),
                        borderwidth=0,
                        padding=(12, 8))
        style.map("Today.TButton",
                 background=[("active", theme["danger"]), ("pressed", theme["danger"])],
                 foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        # Navigation buttons
        style.configure("Nav.TButton", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 14, "bold"),
                        borderwidth=0,
                        padding=(8, 4))
        style.map("Nav.TButton",
                 background=[("active", theme["highlight"]), ("pressed", theme["highlight"])],
                 foreground=[("active", theme["fg"]), ("pressed", theme["fg"])])
        
        # Small navigation buttons
        style.configure("SmallNav.TButton", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 12, "bold"),
                        borderwidth=0,
                        padding=(4, 2))
        style.map("SmallNav.TButton",
                 background=[("active", theme["highlight"]), ("pressed", theme["highlight"])],
                 foreground=[("active", theme["fg"]), ("pressed", theme["fg"])])
        
        # Icon buttons
        style.configure("Icon.TButton", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        borderwidth=0,
                        padding=4)
        style.map("Icon.TButton",
                 background=[("active", theme["highlight"]), ("pressed", theme["highlight"])],
                 foreground=[("active", theme["fg"]), ("pressed", theme["fg"])])
        
        # Header frame
        style.configure("Header.TFrame", 
                        background=theme["header"],
                        borderwidth=0)
        
        # Header label
        style.configure("Header.TLabel", 
                        background=theme["header"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 14, "bold"))
        
        # Title label
        style.configure("Title.TLabel", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 18, "bold"))
        
        # Subtitle label
        style.configure("Subtitle.TLabel", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 14))
        
        # Day header label
        style.configure("DayHeader.TLabel", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 11))
        
        # Today label
        style.configure("Today.TLabel", 
                        background=theme["bg"], 
                        foreground=theme["today"],
                        font=("SF Pro Display", 11, "bold"))
        
        # Calendar cell frame
        style.configure("Cell.TFrame", 
                        background=theme["bg"],
                        borderwidth=1,
                        relief="solid",
                        bordercolor=theme["border"])
        
        # Today cell frame
        style.configure("TodayCell.TFrame", 
                        background=theme["bg"],
                        borderwidth=2,
                        relief="solid",
                        bordercolor=theme["today"])
        
        # Event label
        style.configure("Event.TLabel", 
                        background=theme["accent"],
                        foreground="#ffffff",
                        font=("SF Pro Display", 9),
                        padding=(4, 2))
        
        # Configure other elements
        style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"])
        style.configure("TRadiobutton", background=theme["bg"], foreground=theme["fg"])
        
        # Entry fields
        style.configure("TEntry", 
                        fieldbackground=theme["bg"], 
                        foreground=theme["fg"],
                        borderwidth=1,
                        relief="solid",
                        bordercolor=theme["border"])
        
        # Combobox
        style.configure("TCombobox", 
                        fieldbackground=theme["bg"], 
                        foreground=theme["fg"],
                        borderwidth=1,
                        relief="solid",
                        arrowcolor=theme["fg"])
        style.map("TCombobox",
                 fieldbackground=[("readonly", theme["bg"])],
                 foreground=[("readonly", theme["fg"])])
        
        # Notebook (tabs)
        style.configure("TNotebook", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab", 
                        background=theme["button"], 
                        foreground=theme["fg"],
                        padding=(12, 6),
                        font=("SF Pro Display", 11))
        
        style.map("TNotebook.Tab",
                 background=[("selected", theme["secondary_accent"]), 
                             ("active", theme["button_hover"])],
                 foreground=[("selected", "#ffffff"), 
                             ("active", theme["fg"])])
        
        # Configure the Treeview
        style.configure("Treeview", 
                        background=theme["bg"], 
                        foreground=theme["fg"],
                        fieldbackground=theme["bg"],
                        borderwidth=0,
                        font=("SF Pro Display", 11))
        
        style.map("Treeview",
                 background=[("selected", theme["secondary_accent"])],
                 foreground=[("selected", "#ffffff")])
        
        # Treeview headings
        style.configure("Treeview.Heading", 
                        background=theme["header"], 
                        foreground=theme["fg"],
                        font=("SF Pro Display", 11, "bold"),
                        borderwidth=0)
        
        # Scrollbar
        style.configure("TScrollbar", 
                        background=theme["button"],
                        troughcolor=theme["bg"],
                        borderwidth=0,
                        arrowcolor=theme["fg"])
        
        # Separator
        style.configure("TSeparator", 
                        background=theme["border"])
        
        # Configure the root window
        self.root.configure(background=theme["bg"])
        
        # Update the current theme
        self.current_theme = theme_name
    
    def set_theme(self, theme_name):
        """Set and apply a new theme"""
        self.apply_theme(theme_name)
        self.db_manager.update_setting("theme", theme_name)
    
    def get_event_color(self, index=None, priority=None):
        """Get a color for an event based on index or priority"""
        theme = self.themes[self.current_theme]
        colors = theme["event_colors"]
        
        if priority:
            if priority == "high":
                return theme["danger"]
            elif priority == "medium":
                return theme["warning"]
            elif priority == "low":
                return theme["success"]
        
        if index is not None:
            return colors[index % len(colors)]
            
        # Default color
        return theme["accent"]
