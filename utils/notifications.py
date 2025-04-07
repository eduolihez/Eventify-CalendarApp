from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

# Try to import plyer for notifications
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class NotificationManager:
    """Manages event notifications"""
    
    def __init__(self, db_manager):
        """Initialize the notification manager"""
        self.db_manager = db_manager
        self.notified_events = set()  # Keep track of events we've already notified about
    
    def check_and_notify(self, minutes_before=15):
        """Check for upcoming events and show notifications"""
        # Get events starting in the next X minutes
        upcoming_events = self.db_manager.get_upcoming_events(minutes_before)
        
        for event in upcoming_events:
            # Skip events we've already notified about
            if event["id"] in self.notified_events:
                continue
            
            # Show notification
            self.show_notification(event)
            
            # Add to notified events
            self.notified_events.add(event["id"])
    
    def show_notification(self, event):
        """Show a notification for an event"""
        title = event["title"]
        start_time = datetime.fromisoformat(event["start_time"]).strftime("%H:%M")
        message = f"Event at {start_time}: {title}"
        
        if PLYER_AVAILABLE:
            # Use plyer for system notifications
            notification.notify(
                title="Calendar Event Reminder",
                message=message,
                app_name="Calendar & Event Manager",
                timeout=10
            )
        else:
            # Fallback to a custom notification window
            self.show_custom_notification(title, message)
    
    def show_custom_notification(self, title, message):
        """Show a custom notification window"""
        # Create a toplevel window
        notification_window = tk.Toplevel()
        notification_window.title("Event Reminder")
        notification_window.geometry("300x150+50+50")  # Position near top-left
        notification_window.attributes("-topmost", True)  # Keep on top
        
        # Make it look like a notification
        notification_window.overrideredirect(True)  # Remove window decorations
        notification_window.configure(background="#3498db")
        
        # Add a border
        frame = ttk.Frame(notification_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Add content
        ttk.Label(
            frame, 
            text="Calendar Event Reminder",
            font=("", 12, "bold")
        ).pack(pady=(0, 10))
        
        ttk.Label(
            frame, 
            text=title,
            font=("", 10, "bold")
        ).pack(pady=(0, 5))
        
        ttk.Label(
            frame, 
            text=message,
            wraplength=250
        ).pack(pady=(0, 10))
        
        # Close button
        ttk.Button(
            frame, 
            text="Dismiss",
            command=notification_window.destroy
        ).pack()
        
        # Auto-close after 10 seconds
        notification_window.after(10000, notification_window.destroy)