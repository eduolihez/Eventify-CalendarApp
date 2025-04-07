import tkinter as tk
from tkinter import ttk
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import locale
import gettext

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from ui.app import CalendarApp

def setup_database():
    """Initialize the database if it doesn't exist"""
    db_manager = DatabaseManager()
    db_manager.setup_database()
    return db_manager

def main():
    """Main application entry point"""
    # Create the root window
    root = tk.Tk()
    root.title("Calendar & Event Manager")
    root.geometry("1280x800")
    
    # Set application icon (using emoji as placeholder)
    try:
        # Try to set a window icon
        root.iconbitmap("calendar_icon.ico")  # You would need to create this icon file
    except:
        # If icon file is not available, just continue
        pass
    
    # Set up the database
    db_manager = setup_database()
    
    # Initialize and run the application
    app = CalendarApp(root, db_manager)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()

