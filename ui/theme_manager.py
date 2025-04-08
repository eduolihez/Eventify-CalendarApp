import tkinter as tk
from tkinter import ttk
import os


class ThemeManager:
    """Manages application themes (light/dark)"""

    def __init__(self, root, db_manager):
        """Initialize the theme manager"""
        self.root = root
        self.db_manager = db_manager

        # Define blue-themed color palettes
        self.themes = {
            "light": {
                "bg": "#f5f9ff",  # Very light blue background
                "fg": "#2c3e50",  # Dark blue-gray text
                "accent": "#3498db",  # Primary blue
                "secondary_accent": "#2980b9",  # Darker blue
                "tertiary_accent": "#5dade2",  # Lighter blue
                "success": "#2ecc71",  # Green
                "warning": "#f39c12",  # Orange
                "danger": "#e74c3c",  # Red
                "button": "#e8f4fc",  # Very light blue button
                "button_hover": "#d6eaf8",  # Slightly darker button hover
                "highlight": "#d6eaf8",  # Light blue highlight
                "border": "#bdc3c7",  # Light gray border
                "card": "#ffffff",  # White card background
                "header": "#e8f4fc",  # Light blue header
                "today": "#3498db",  # Blue for today highlight
                "event_colors": [
                    "#3498db",  # Blue
                    "#2980b9",  # Darker blue
                    "#1abc9c",  # Teal
                    "#2ecc71",  # Green
                    "#9b59b6",  # Purple
                    "#34495e",  # Dark blue-gray
                    "#5dade2",  # Light blue
                    "#f1c40f",  # Yellow
                ],
            },
            "dark": {
                "bg": "#1a2530",  # Dark blue-gray background
                "fg": "#ecf0f1",  # Off-white text
                "accent": "#3498db",  # Primary blue
                "secondary_accent": "#5dade2",  # Lighter blue
                "tertiary_accent": "#85c1e9",  # Even lighter blue
                "success": "#2ecc71",  # Green
                "warning": "#f39c12",  # Orange
                "danger": "#e74c3c",  # Red
                "button": "#2c3e50",  # Dark blue-gray button
                "button_hover": "#34495e",  # Slightly lighter button hover
                "highlight": "#34495e",  # Dark blue-gray highlight
                "border": "#7f8c8d",  # Medium gray border
                "card": "#2c3e50",  # Dark blue-gray card
                "header": "#2c3e50",  # Dark blue-gray header
                "today": "#3498db",  # Blue for today highlight
                "event_colors": [
                    "#3498db",  # Blue
                    "#5dade2",  # Lighter blue
                    "#1abc9c",  # Teal
                    "#2ecc71",  # Green
                    "#9b59b6",  # Purple
                    "#85c1e9",  # Very light blue
                    "#5dade2",  # Light blue
                    "#f1c40f",  # Yellow
                ],
            },
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

        # Blue-styled buttons
        style.configure(
            "iOS.TButton",
            background=theme["accent"],
            foreground="#ffffff",
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
            padding=(12, 8),
        )
        style.map(
            "iOS.TButton",
            background=[
                ("active", theme["secondary_accent"]),
                ("pressed", theme["secondary_accent"]),
            ],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )

        # Secondary blue-styled buttons
        style.configure(
            "iOS.Secondary.TButton",
            background=theme["button"],
            foreground=theme["accent"],
            font=("SF Pro Display", 11, "bold"),
            borderwidth=1,
            padding=(12, 8),
        )
        style.map(
            "iOS.Secondary.TButton",
            background=[
                ("active", theme["button_hover"]),
                ("pressed", theme["button_hover"]),
            ],
            foreground=[("active", theme["accent"]), ("pressed", theme["accent"])],
        )

        # Today button
        style.configure(
            "Today.TButton",
            background=theme["accent"],
            foreground="#ffffff",
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
            padding=(12, 8),
        )
        style.map(
            "Today.TButton",
            background=[
                ("active", theme["secondary_accent"]),
                ("pressed", theme["secondary_accent"]),
            ],
            foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
        )

        # Navigation buttons
        style.configure(
            "Nav.TButton",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("SF Pro Display", 14, "bold"),
            borderwidth=0,
            padding=(8, 4),
        )
        style.map(
            "Nav.TButton",
            background=[
                ("active", theme["highlight"]),
                ("pressed", theme["highlight"]),
            ],
            foreground=[("active", theme["fg"]), ("pressed", theme["fg"])],
        )

        # Small navigation buttons
        style.configure(
            "SmallNav.TButton",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("SF Pro Display", 12, "bold"),
            borderwidth=0,
            padding=(4, 2),
        )
        style.map(
            "SmallNav.TButton",
            background=[
                ("active", theme["highlight"]),
                ("pressed", theme["highlight"]),
            ],
            foreground=[("active", theme["fg"]), ("pressed", theme["fg"])],
        )

        # Icon buttons
        style.configure(
            "Icon.TButton",
            background=theme["bg"],
            foreground=theme["fg"],
            borderwidth=0,
            padding=4,
        )
        style.map(
            "Icon.TButton",
            background=[
                ("active", theme["highlight"]),
                ("pressed", theme["highlight"]),
            ],
            foreground=[("active", theme["fg"]), ("pressed", theme["fg"])],
        )

        # Header frame
        style.configure("Header.TFrame", background=theme["header"], borderwidth=0)

        # Header label
        style.configure(
            "Header.TLabel",
            background=theme["header"],
            foreground=theme["fg"],
            font=("SF Pro Display", 14, "bold"),
        )

        # Title label
        style.configure(
            "Title.TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("SF Pro Display", 18, "bold"),
        )

        # Subtitle label
        style.configure(
            "Subtitle.TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("SF Pro Display", 14),
        )

        # Day header label
        style.configure(
            "DayHeader.TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=("SF Pro Display", 11),
        )

        # Today label
        style.configure(
            "Today.TLabel",
            background=theme["bg"],
            foreground=theme["accent"],
            font=("SF Pro Display", 11, "bold"),
        )

        # Calendar cell frame
        style.configure(
            "Cell.TFrame",
            background=theme["card"],
            borderwidth=1,
            relief="solid",
            bordercolor=theme["border"],
        )

        # Today cell frame
        style.configure(
            "TodayCell.TFrame",
            background=theme["card"],
            borderwidth=2,
            relief="solid",
            bordercolor=theme["accent"],
        )

        # Event label
        style.configure(
            "Event.TLabel",
            background=theme["accent"],
            foreground="#ffffff",
            font=("SF Pro Display", 9),
            padding=(4, 2),
        )

        # Configure other elements
        style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"])
        style.configure("TRadiobutton", background=theme["bg"], foreground=theme["fg"])

        # Entry fields
        style.configure(
            "TEntry",
            fieldbackground=theme["card"],
            foreground=theme["fg"],
            borderwidth=1,
            relief="solid",
            bordercolor=theme["border"],
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=theme["card"],
            foreground=theme["fg"],
            borderwidth=1,
            relief="solid",
            arrowcolor=theme["fg"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["card"])],
            foreground=[("readonly", theme["fg"])],
        )

        # Notebook (tabs)
        style.configure(
            "TNotebook",
            background=theme["bg"],
            foreground=theme["fg"],
            tabmargins=[2, 5, 2, 0],
        )

        style.configure(
            "TNotebook.Tab",
            background=theme["button"],
            foreground=theme["fg"],
            padding=(12, 6),
            font=("SF Pro Display", 11),
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", theme["accent"]),
                ("active", theme["button_hover"]),
            ],
            foreground=[("selected", "#ffffff"), ("active", theme["fg"])],
        )

        # Configure the Treeview
        style.configure(
            "Treeview",
            background=theme["card"],
            foreground=theme["fg"],
            fieldbackground=theme["card"],
            borderwidth=0,
            font=("SF Pro Display", 11),
        )

        style.map(
            "Treeview",
            background=[("selected", theme["accent"])],
            foreground=[("selected", "#ffffff")],
        )

        # Treeview headings
        style.configure(
            "Treeview.Heading",
            background=theme["header"],
            foreground=theme["fg"],
            font=("SF Pro Display", 11, "bold"),
            borderwidth=0,
        )

        # Scrollbar
        style.configure(
            "TScrollbar",
            background=theme["button"],
            troughcolor=theme["bg"],
            borderwidth=0,
            arrowcolor=theme["fg"],
        )

        # Separator
        style.configure("TSeparator", background=theme["border"])

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
