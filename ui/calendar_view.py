import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, timedelta
import locale

class BaseCalendarView(ttk.Frame):
    """Base class for calendar views"""
    
    def __init__(self, parent, db_manager, app):
        super().__init__(parent)
        self.db_manager = db_manager
        self.app = app
        self._ = app.i18n.gettext
        
        # Set the current date to today
        self.current_date = datetime.now()
        
        # Initialize the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components - to be implemented by subclasses"""
        pass
    
    def refresh(self):
        """Refresh the view - to be implemented by subclasses"""
        pass
    
    def get_current_date(self):
        """Get the current date being displayed"""
        return self.current_date
    
    def get_date_range(self):
        """Get the date range being displayed - to be implemented by subclasses"""
        pass
    
    def go_to_today(self):
        """Navigate to today's date"""
        self.current_date = datetime.now()
        self.refresh()


class MonthView(BaseCalendarView):
    """Monthly calendar view"""
    
    def setup_ui(self):
        """Set up the monthly view UI"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Header
        self.rowconfigure(1, weight=1)  # Calendar grid
        
        # Create the calendar grid
        self.calendar_frame = ttk.Frame(self, style="TFrame")
        self.calendar_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        
        # Create day labels (Mon, Tue, etc.)
        self.day_labels = []
        days_header = ttk.Frame(self, style="TFrame")
        days_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        days = [self._("Mon"), self._("Tue"), self._("Wed"), self._("Thu"), 
                self._("Fri"), self._("Sat"), self._("Sun")]
        
        for i, day in enumerate(days):
            label = ttk.Label(days_header, text=day, anchor="center", style="DayHeader.TLabel")
            label.grid(row=0, column=i, padx=2, pady=5, sticky="ew")
            days_header.columnconfigure(i, weight=1)
            self.day_labels.append(label)
        
        # Initial refresh
        self.refresh()
    
    def refresh(self):
        """Refresh the month view"""
        # Clear the calendar frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Get the month calendar
        year = self.current_date.year
        month = self.current_date.month
        
        # Get the first day of the month and the number of days
        first_day = datetime(year, month, 1)
        _, num_days = calendar.monthrange(year, month)
        
        # Adjust for Monday as the first day of the week (0 = Monday in our grid)
        first_weekday = first_day.weekday()
        
        # Get events for this month
        start_date = first_day.strftime("%Y-%m-%d 00:00:00")
        end_date = datetime(year, month, num_days, 23, 59, 59).strftime("%Y-%m-%d 23:59:59")
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        # Create a dictionary to store events by day
        events_by_day = {}
        for event in events:
            event_date = datetime.fromisoformat(event["start_time"]).day
            if event_date not in events_by_day:
                events_by_day[event_date] = []
            events_by_day[event_date].append(event)
        
        # Create the calendar grid
        day = 1
        for week in range(6):  # Maximum of 6 weeks in a month view
            if day > num_days:
                break
                
            for weekday in range(7):  # 7 days in a week
                if week == 0 and weekday < first_weekday:
                    # Empty cell before the first day of the month
                    cell = ttk.Frame(self.calendar_frame, style="Cell.TFrame")
                    cell.grid(row=week, column=weekday, sticky="nsew", padx=2, pady=2)
                    self.calendar_frame.columnconfigure(weekday, weight=1)
                    self.calendar_frame.rowconfigure(week, weight=1)
                elif day <= num_days:
                    # Create a day cell
                    cell = self.create_day_cell(week, weekday, day, events_by_day.get(day, []))
                    day += 1
                else:
                    # Empty cell after the last day of the month
                    cell = ttk.Frame(self.calendar_frame, style="Cell.TFrame")
                    cell.grid(row=week, column=weekday, sticky="nsew", padx=2, pady=2)
    
    def create_day_cell(self, week, weekday, day, events):
        """Create a cell for a specific day with its events"""
        # Check if this is today
        is_today = (self.current_date.year == datetime.now().year and 
                   self.current_date.month == datetime.now().month and 
                   day == datetime.now().day)
        
        # Create the cell frame with appropriate style
        cell_style = "TodayCell.TFrame" if is_today else "Cell.TFrame"
        cell = ttk.Frame(self.calendar_frame, style=cell_style)
        cell.grid(row=week, column=weekday, sticky="nsew", padx=2, pady=2)
        
        # Configure the cell to be responsive
        cell.columnconfigure(0, weight=1)
        
        # Create a header frame for the day number
        day_header = ttk.Frame(cell, style="TFrame")
        day_header.grid(row=0, column=0, sticky="new", padx=2, pady=2)
        
        # Day number label with special styling for today
        day_label_style = "Today.TLabel" if is_today else "TLabel"
        
        # Create a circular background for the day number if it's today
        if is_today:
            # Create a canvas for the circular background
            day_canvas = tk.Canvas(day_header, width=28, height=28, 
                                  bg=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"], 
                                  highlightthickness=0)
            day_canvas.pack(side=tk.LEFT, padx=4, pady=2)
            
            # Draw the circle
            day_canvas.create_oval(2, 2, 26, 26, 
                                  fill=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["today"], 
                                  outline="")
            
            # Add the day number
            day_canvas.create_text(14, 14, text=str(day), fill="white", font=("SF Pro Display", 11, "bold"))
        else:
            day_label = ttk.Label(
                day_header, 
                text=str(day),
                style=day_label_style
            )
            day_label.pack(side=tk.LEFT, padx=6, pady=2)
        
        # Add events to the cell
        event_frame = ttk.Frame(cell, style="TFrame")
        event_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        
        # Sort events by start time
        events.sort(key=lambda e: e["start_time"])
        
        # Display up to 3 events, with a "more" indicator if there are more
        max_events = 3
        for i, event in enumerate(events[:max_events]):
            event_time = datetime.fromisoformat(event["start_time"]).strftime("%H:%M")
            
            # Get color based on priority or use a color from the palette
            event_color = event.get("color", self.app.theme_manager.get_event_color(i, event.get("priority")))
            
            # Create a container for the event
            event_container = tk.Frame(
                event_frame,
                background=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
                borderwidth=0,
                highlightthickness=0
            )
            event_container.grid(row=i, column=0, sticky="ew", pady=1)
            event_frame.columnconfigure(0, weight=1)
            
            # Create the event with rounded corners using a Canvas
            event_height = 22
            event_canvas = tk.Canvas(
                event_container, 
                height=event_height,
                bg=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
                highlightthickness=0
            )
            event_canvas.pack(fill=tk.X, expand=True)
            
            # Calculate width based on parent
            event_container.update_idletasks()
            event_width = event_container.winfo_width()
            if event_width < 2:  # If not yet rendered, use a default
                event_width = 100
            
            event_canvas.config(width=event_width)
            
            # Function to create rounded rectangle
            def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
                points = [
                    x1+radius, y1,
                    x2-radius, y1,
                    x2, y1,
                    x2, y1+radius,
                    x2, y2-radius,
                    x2, y2,
                    x2-radius, y2,
                    x1+radius, y2,
                    x1, y2,
                    x1, y2-radius,
                    x1, y1+radius,
                    x1, y1
                ]
                return canvas.create_polygon(points, smooth=True, **kwargs)
            
            # Draw the rounded rectangle
            event_rect = create_rounded_rectangle(
                event_canvas, 2, 0, event_width-2, event_height, 
                radius=6, fill=event_color, outline=""
            )
            
            # Add text
            event_text = f"{event_time} {event['title']}"
            event_text_id = event_canvas.create_text(
                10, event_height/2, 
                text=event_text, 
                fill="white", 
                font=("SF Pro Display", 9),
                anchor="w"
            )
            
            # Add hover effect
            def on_enter(e, rect=event_rect, canvas=event_canvas, color=event_color):
                # Darken the color slightly
                r, g, b = canvas.winfo_rgb(color)
                darker = f'#{int(r/65535*0.9):02x}{int(g/65535*0.9):02x}{int(b/65535*0.9):02x}'
                canvas.itemconfig(rect, fill=darker)
                
            def on_leave(e, rect=event_rect, canvas=event_canvas, color=event_color):
                canvas.itemconfig(rect, fill=color)
            
            event_canvas.bind("<Enter>", on_enter)
            event_canvas.bind("<Leave>", on_leave)
            
            # Bind click event to open the event
            event_canvas.bind("<Button-1>", lambda e, eid=event["id"]: self.app.edit_event(eid))
        
        # Show "more" indicator if there are more events
        if len(events) > max_events:
            more_container = tk.Frame(
                event_frame,
                background=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
                borderwidth=0,
                highlightthickness=0
            )
            more_container.grid(row=max_events, column=0, sticky="ew", pady=1)
            
            more_label = ttk.Label(
                more_container,
                text=self._("+ {} more").format(len(events) - max_events),
                style="TLabel",
                font=("SF Pro Display", 8),
                foreground=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["secondary_accent"]
            )
            more_label.pack(side=tk.LEFT, padx=5)
            
            # Bind click to show all events for this day
            more_label.bind("<Button-1>", lambda e, d=day: self.show_day_events(d))
            more_container.bind("<Button-1>", lambda e, d=day: self.show_day_events(d))
        
        # Make the entire cell clickable to add a new event
        cell.bind("<Double-1>", lambda e: self.add_event_on_day(day))
        
        return cell
    
    def add_event_on_day(self, day):
        """Open the event form pre-filled with the selected day"""
        # Create a datetime for the selected day
        selected_date = datetime(
            self.current_date.year,
            self.current_date.month,
            day,
            datetime.now().hour,
            0  # Start at the beginning of the hour
        )
        
        # Pre-fill event data
        event_data = {
            "start_time": selected_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (selected_date + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Open the event form
        from ui.event_form import EventForm
        EventForm(self.app.root, self.db_manager, self.app, event_data=event_data, callback=self.refresh)
    
    def show_day_events(self, day):
        """Show all events for a specific day"""
        # Create a datetime for the selected day
        selected_date = datetime(self.current_date.year, self.current_date.month, day)
        
        # Get the date range for the entire day
        start_date = selected_date.strftime("%Y-%m-%d 00:00:00")
        end_date = selected_date.strftime("%Y-%m-%d 23:59:59")
        
        # Get events for this day
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        if not events:
            return
        
        # Create a new window to display the events
        day_window = tk.Toplevel(self.app.root)
        day_window.title(self._("Events for {}").format(selected_date.strftime("%B %d, %Y")))
        day_window.geometry("550x500")
        day_window.transient(self.app.root)
        day_window.grab_set()
        
        # Apply theme
        day_window.configure(bg=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"])
        
        # Create a header
        header_frame = ttk.Frame(day_window, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(
            header_frame, 
            text=selected_date.strftime("%B %d, %Y"),
            style="Title.TLabel"
        ).pack(side=tk.LEFT)
        
        # Create a frame for the events
        events_frame = ttk.Frame(day_window, style="TFrame")
        events_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create a canvas with scrollbar for the events
        canvas = tk.Canvas(
            events_frame, 
            bg=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create a frame inside the canvas to hold the events
        events_list_frame = ttk.Frame(canvas, style="TFrame")
        canvas.create_window((0, 0), window=events_list_frame, anchor="nw")
        
        # Add events to the list
        for i, event in enumerate(sorted(events, key=lambda e: e["start_time"])):
            # Create an event card
            event_card = ttk.Frame(
                events_list_frame, 
                style="Cell.TFrame",
                padding=15
            )
            event_card.pack(fill=tk.X, pady=8)
            
            # Event time
            start_time = datetime.fromisoformat(event["start_time"])
            end_time = datetime.fromisoformat(event["end_time"])
            
            time_str = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            
            # Get color based on priority or use a color from the palette
            event_color = event.get("color", self.app.theme_manager.get_event_color(i, event.get("priority")))
            
            # Color indicator
            color_indicator = tk.Frame(
                event_card, 
                width=6, 
                background=event_color
            )
            color_indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
            
            # Event details
            details_frame = ttk.Frame(event_card, style="TFrame")
            details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            ttk.Label(
                details_frame, 
                text=event["title"],
                style="TLabel",
                font=("SF Pro Display", 13, "bold")
            ).pack(anchor="w")
            
            ttk.Label(
                details_frame, 
                text=time_str,
                style="TLabel",
                foreground=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["secondary_accent"]
            ).pack(anchor="w", pady=(2, 0))
            
            if event.get("location"):
                ttk.Label(
                    details_frame, 
                    text=event["location"],
                    style="TLabel",
                    foreground=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["fg"]
                ).pack(anchor="w", pady=(5, 0))
            
            if event.get("description"):
                desc_text = event["description"]
                if len(desc_text) > 100:
                    desc_text = desc_text[:97] + "..."
                
                ttk.Label(
                    details_frame, 
                    text=desc_text,
                    style="TLabel",
                    foreground=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["fg"],
                    wraplength=350
                ).pack(anchor="w", pady=(5, 0))
            
            # Edit button
            edit_btn = ttk.Button(
                event_card, 
                text=self._("Edit"),
                style="iOS.Secondary.TButton",
                command=lambda eid=event["id"]: self.app.edit_event(eid)
            )
            edit_btn.pack(side=tk.RIGHT, padx=5)
            
            # Bind double-click to edit
            event_card.bind("<Double-1>", lambda e, eid=event["id"]: self.app.edit_event(eid))
        
        # Update the canvas scroll region
        events_list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(day_window, style="TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Button(
            button_frame, 
            text=self._("Add Event"),
            style="iOS.TButton",
            command=lambda: self.add_event_on_day(day)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text=self._("Close"),
            style="iOS.Secondary.TButton",
            command=day_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def on_event_double_click(self, tree):
        """Handle double-click on an event in the day view"""
        selected_item = tree.selection()
        if selected_item:
            event_id = int(tree.item(selected_item[0], "tags")[0])
            self.app.edit_event(event_id)
    
    def previous_month(self):
        """Navigate to the previous month"""
        year = self.current_date.year
        month = self.current_date.month
        
        if month == 1:
            self.current_date = self.current_date.replace(year=year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=month-1)
        
        self.refresh()
    
    def next_month(self):
        """Navigate to the next month"""
        year = self.current_date.year
        month = self.current_date.month
        
        if month == 12:
            self.current_date = self.current_date.replace(year=year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=month+1)
        
        self.refresh()
    
    def get_date_range(self):
        """Get the date range for the current month view"""
        year = self.current_date.year
        month = self.current_date.month
        
        # First day of the month
        first_day = datetime(year, month, 1)
        
        # Last day of the month
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return (
            first_day.strftime("%Y-%m-%d 00:00:00"),
            last_day.strftime("%Y-%m-%d 23:59:59")
        )


class WeekView(BaseCalendarView):
    """Weekly calendar view"""
    
    def setup_ui(self):
        """Set up the weekly view UI"""
        self.columnconfigure(1, weight=1)  # Calendar grid
        self.rowconfigure(0, weight=0)  # Header
        self.rowconfigure(1, weight=1)  # Calendar grid
        
        # Create time labels column
        time_frame = ttk.Frame(self, style="TFrame")
        time_frame.grid(row=1, column=0, sticky="ns", padx=(15, 0), pady=10)
        
        # Create time labels (00:00, 01:00, etc.)
        for hour in range(24):
            label = ttk.Label(
                time_frame, 
                text=f"{hour:02d}:00",
                width=6,
                style="TLabel",
                anchor="e"
            )
            label.grid(row=hour, column=0, padx=5, pady=5, sticky="n")
            time_frame.rowconfigure(hour, weight=1)
        
        # Create the calendar grid
        self.calendar_frame = ttk.Frame(self, style="TFrame")
        self.calendar_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=10)
        
        # Create day headers (Mon, Tue, etc.)
        days_header = ttk.Frame(self, style="Header.TFrame")
        days_header.grid(row=0, column=1, sticky="ew", padx=15, pady=(10, 5))
        
        self.day_labels = []
        for i in range(7):
            label = ttk.Label(days_header, text="", anchor="center", style="Header.TLabel")
            label.grid(row=0, column=i, padx=2, pady=5, sticky="ew")
            days_header.columnconfigure(i, weight=1)
            self.day_labels.append(label)
        
        # Initial refresh
        self.refresh()
    
    def refresh(self):
        """Refresh the week view"""
        # Clear the calendar frame
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Get the week dates
        week_start, week_end, week_dates = self.get_week_dates()
        
        # Update day headers
        for i, date in enumerate(week_dates):
            day_name = date.strftime("%a")
            day_num = date.day
            month_abbr = date.strftime("%b") if date.day == 1 or i == 0 else ""
            
            # Highlight today
            is_today = (date.year == datetime.now().year and 
                       date.month == datetime.now().month and 
                       date.day == datetime.now().day)
            
            header_style = "Today.TLabel" if is_today else "Header.TLabel"
            
            self.day_labels[i].configure(
                text=f"{day_name} {day_num} {month_abbr}",
                style=header_style
            )
        
        # Get events for this week
        start_date = week_start.strftime("%Y-%m-%d 00:00:00")
        end_date = week_end.strftime("%Y-%m-%d 23:59:59")
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        # Create the week grid
        for day in range(7):
            # Check if this column is today
            is_today_column = (week_dates[day].year == datetime.now().year and 
                              week_dates[day].month == datetime.now().month and 
                              week_dates[day].day == datetime.now().day)
            
            day_column = ttk.Frame(self.calendar_frame, style="TFrame")
            day_column.grid(row=0, column=day, sticky="nsew", padx=2)
            self.calendar_frame.columnconfigure(day, weight=1)
            
            # Create hour cells for this day
            for hour in range(24):
                cell_style = "TodayCell.TFrame" if is_today_column else "Cell.TFrame"
                cell = ttk.Frame(day_column, style=cell_style, height=60)
                cell.grid(row=hour, column=0, sticky="nsew", pady=1)
                day_column.rowconfigure(hour, weight=1)
                
                # Add a thin horizontal line at the top of each cell
                separator = ttk.Separator(cell, orient="horizontal")
                separator.place(relx=0, rely=0, relwidth=1, height=1)
                
                # Make the cell clickable to add a new event
                cell.bind("<Double-1>", lambda e, d=day, h=hour: self.add_event_on_hour(d, h))
        
        # Add events to the grid
        for event in events:
            self.add_event_to_grid(event, week_dates)
    
    def add_event_to_grid(self, event, week_dates):
        """Add an event to the week grid"""
        start_time = datetime.fromisoformat(event["start_time"])
        end_time = datetime.fromisoformat(event["end_time"])
        
        # Check if the event is in this week
        event_date = start_time.date()
        for day_idx, day_date in enumerate(week_dates):
            if event_date == day_date.date():
                # Calculate position and size
                start_hour = start_time.hour + start_time.minute / 60
                end_hour = end_time.hour + end_time.minute / 60
                
                # Handle multi-day events
                if end_time.date() > start_time.date():
                    end_hour = 24.0
                
                # Create event widget
                day_column = self.calendar_frame.winfo_children()[day_idx]
                
                # Calculate which hour cell to place it in and the height
                start_cell = int(start_hour)
                height_cells = max(1, end_hour - start_hour)
                
                # Get color based on priority or use a color from the palette
                event_color = event.get("color", self.app.theme_manager.get_event_color(day_idx, event.get("priority")))
                
                # Create a frame for the event with rounded corners
                event_frame = tk.Frame(
                    day_column,
                    background=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
                    borderwidth=0,
                    highlightthickness=0
                )
                
                # Position the event
                top_position = start_hour - start_cell
                height_percent = min(1.0, height_cells)
                
                event_frame.place(
                    relx=0.05,
                    rely=top_position / 1.0 + start_cell / 24.0,
                    relwidth=0.9,
                    relheight=height_percent / 24.0
                )
                
                # Create a canvas for the rounded rectangle
                event_canvas = tk.Canvas(
                    event_frame,
                    bg=self.app.theme_manager.themes[self.app.theme_manager.current_theme]["bg"],
                    highlightthickness=0
                )
                event_canvas.pack(fill=tk.BOTH, expand=True)
                
                # Function to create rounded rectangle
                def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
                    points = [
                        x1+radius, y1,
                        x2-radius, y1,
                        x2, y1,
                        x2, y1+radius,
                        x2, y2-radius,
                        x2, y2,
                        x2-radius, y2,
                        x1+radius, y2,
                        x1, y2,
                        x1, y2-radius,
                        x1, y1+radius,
                        x1, y1
                    ]
                    return canvas.create_polygon(points, smooth=True, **kwargs)
                
                # Draw the rounded rectangle
                event_frame.update_idletasks()
                width = event_frame.winfo_width()
                height = event_frame.winfo_height()
                
                if width > 0 and height > 0:
                    event_rect = create_rounded_rectangle(
                        event_canvas, 0, 0, width, height, 
                        radius=8, fill=event_color, outline=""
                    )
                
                    # Add event details
                    event_title = tk.Label(
                        event_canvas,
                        text=f"{start_time.strftime('%H:%M')} {event['title']}",
                        background=event_color,
                        foreground="white",
                        anchor="w",
                        font=("SF Pro Display", 9),
                        padx=6,
                        pady=2
                    )
                    event_title.place(relx=0, rely=0, relwidth=1, relheight=1)
                    
                    # Add hover effect
                    def on_enter(e, rect=event_rect, canvas=event_canvas, color=event_color, label=event_title):
                        # Darken the color slightly
                        r, g, b = canvas.winfo_rgb(color)
                        darker = f'#{int(r/65535*0.9):02x}{int(g/65535*0.9):02x}{int(b/65535*0.9):02x}'
                        canvas.itemconfig(rect, fill=darker)
                        label.config(background=darker)
                        
                    def on_leave(e, rect=event_rect, canvas=event_canvas, color=event_color, label=event_title):
                        canvas.itemconfig(rect, fill=color)
                        label.config(background=color)
                    
                    event_canvas.bind("<Enter>", on_enter)
                    event_canvas.bind("<Leave>", on_leave)
                    event_title.bind("<Enter>", on_enter)
                    event_title.bind("<Leave>", on_leave)
                
                # Bind click event to open the event
                event_canvas.bind("<Button-1>", lambda e, eid=event["id"]: self.app.edit_event(eid))
                event_title.bind("<Button-1>", lambda e, eid=event["id"]: self.app.edit_event(eid))
                
                # If the event spans multiple days, add it to the next day too
                if end_time.date() > start_time.date() and day_idx < 6:
                    next_day_event = event.copy()
                    next_day_start = datetime.combine(
                        week_dates[day_idx + 1].date(),
                        datetime.min.time()
                    )
                    next_day_event["start_time"] = next_day_start.isoformat()
                    
                    # Recursively add to the next day
                    self.add_event_to_grid(next_day_event, week_dates)
                
                break
    
    def add_event_on_hour(self, day, hour):
        """Open the event form pre-filled with the selected day and hour"""
        # Get the date for the selected day
        _, _, week_dates = self.get_week_dates()
        selected_date = week_dates[day]
        
        # Create a datetime for the selected hour
        selected_datetime = datetime(
            selected_date.year,
            selected_date.month,
            selected_date.day,
            hour,
            0  # Start at the beginning of the hour
        )
        
        # Pre-fill event data
        event_data = {
            "start_time": selected_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (selected_datetime + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Open the event form
        from ui.event_form import EventForm
        EventForm(self.app.root, self.db_manager, self.app, event_data=event_data, callback=self.refresh)
    
    def get_week_dates(self):
        """Get the dates for the current week"""
        # Get the first day of the week (Monday)
        current_weekday = self.current_date.weekday()
        week_start = self.current_date - timedelta(days=current_weekday)
        week_start = datetime(week_start.year, week_start.month, week_start.day)
        
        # Get the last day of the week (Sunday)
        week_end = week_start + timedelta(days=6)
        
        # Get all dates in the week
        week_dates = [week_start + timedelta(days=i) for i in range(7)]
        
        return week_start, week_end, week_dates
    
    def previous_week(self):
        """Navigate to the previous week"""
        self.current_date -= timedelta(days=7)
        self.refresh()
    
    def next_week(self):
        """Navigate to the next week"""
        self.current_date += timedelta(days=7)
        self.refresh()
    
    def get_date_range(self):
        """Get the date range for the current week view"""
        week_start, week_end, _ = self.get_week_dates()
        
        return (
            week_start.strftime("%Y-%m-%d 00:00:00"),
            week_end.strftime("%Y-%m-%d 23:59:59")
        )
