import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, timedelta
import calendar
import gettext

# Import our modules
from ui.calendar_view import MonthView, WeekView
from ui.event_form import EventForm
from ui.theme_manager import ThemeManager
from utils.notifications import NotificationManager
from utils.import_export import ImportExportManager
from utils.i18n import I18nManager
from utils.shortcuts import ShortcutManager


class CalendarApp:
    """Main application class that manages the UI and interactions"""

    def __init__(self, root, db_manager):
        """Initialize the application"""
        self.root = root
        self.db_manager = db_manager

        # Set up internationalization
        self.i18n = I18nManager(self.db_manager.get_setting("language") or "en")
        self._ = self.i18n.gettext

        # Set up theme manager
        self.theme_manager = ThemeManager(self.root, self.db_manager)

        # Set up notification manager
        self.notification_manager = NotificationManager(self.db_manager)

        # Set up import/export manager
        self.import_export_manager = ImportExportManager(self.db_manager)

        # Set up shortcut manager
        self.shortcut_manager = ShortcutManager(self)

        # Initialize UI components
        self.setup_ui()

        # Start notification checker
        self.check_notifications()

    def setup_ui(self):
        """Set up the main UI components"""
        # Configure the root window to be responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Menu bar
        self.root.rowconfigure(1, weight=0)  # Toolbar
        self.root.rowconfigure(2, weight=1)  # Main content
        self.root.rowconfigure(3, weight=0)  # Status bar

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create main content area with notebook for different views
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)

        # Create month view
        self.month_view = MonthView(self.notebook, self.db_manager, self)
        self.notebook.add(self.month_view, text=self._("Month"))

        # Create week view
        self.week_view = WeekView(self.notebook, self.db_manager, self)
        self.notebook.add(self.week_view, text=self._("Week"))

        # Create status bar with blue gradient background
        status_frame = ttk.Frame(self.root, style="Header.TFrame")
        status_frame.grid(row=3, column=0, sticky="ew")

        # Create a canvas for the gradient background
        status_canvas = tk.Canvas(
            status_frame,
            height=36,
            bg=self.theme_manager.themes[self.theme_manager.current_theme]["header"],
            highlightthickness=0,
        )
        status_canvas.pack(fill=tk.X, expand=True)

        # Create gradient
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        status_canvas.update_idletasks()
        width = status_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 1000

        # Create gradient from left to right
        for i in range(width):
            # Calculate color based on position
            r1, g1, b1 = status_canvas.winfo_rgb(theme["header"])
            r2, g2, b2 = status_canvas.winfo_rgb(theme["accent"])

            # Adjust the gradient to be subtle
            ratio = i / width * 0.2  # Only go 20% toward the accent color
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            status_canvas.create_line(i, 0, i, 36, fill=color)

        # Status text
        self.status_var = tk.StringVar()
        self.status_var.set(self._("Ready"))

        status_canvas.create_text(
            20,
            18,
            text=self.status_var.get(),
            fill=theme["fg"],
            font=("SF Pro Display", 11),
            anchor="w",
            tags="status_text",
        )

        # Update status text when variable changes
        def update_status(*args):
            status_canvas.itemconfig("status_text", text=self.status_var.get())

        self.status_var.trace_add("write", update_status)

        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Register keyboard shortcuts
        self.register_shortcuts()

        # Update the period label
        self.update_period_label()

    def create_menu_bar(self):
        """Create the application menu bar"""
        self.menu_bar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(
            label=self._("New Event"), command=self.create_event, accelerator="Ctrl+N"
        )
        file_menu.add_separator()
        file_menu.add_command(label=self._("Import Events"), command=self.import_events)
        file_menu.add_command(label=self._("Export Events"), command=self.export_events)
        file_menu.add_separator()
        file_menu.add_command(
            label=self._("Exit"), command=self.root.quit, accelerator="Alt+F4"
        )
        self.menu_bar.add_cascade(label=self._("File"), menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(
            label=self._("Search Events"),
            command=self.search_events,
            accelerator="Ctrl+F",
        )
        self.menu_bar.add_cascade(label=self._("Edit"), menu=edit_menu)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(
            label=self._("Go to Today"), command=self.go_to_today, accelerator="Ctrl+T"
        )
        view_menu.add_separator()

        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_command(
            label=self._("Light Blue Theme"), command=lambda: self.change_theme("light")
        )
        theme_menu.add_command(
            label=self._("Dark Blue Theme"), command=lambda: self.change_theme("dark")
        )
        view_menu.add_cascade(label=self._("Theme"), menu=theme_menu)

        # Language submenu
        language_menu = tk.Menu(view_menu, tearoff=0)
        language_menu.add_command(
            label="English", command=lambda: self.change_language("en")
        )
        language_menu.add_command(
            label="Español", command=lambda: self.change_language("es")
        )
        view_menu.add_cascade(label=self._("Language"), menu=language_menu)

        self.menu_bar.add_cascade(label=self._("View"), menu=view_menu)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label=self._("About"), command=self.show_about)
        self.menu_bar.add_cascade(label=self._("Help"), menu=help_menu)

        self.root.config(menu=self.menu_bar)

    def create_toolbar(self):
        """Create the application toolbar"""
        theme = self.theme_manager.themes[self.theme_manager.current_theme]

        # Create a frame for the toolbar with a gradient background
        toolbar_frame = tk.Frame(self.root, bg=theme["bg"])
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # Create a canvas for the gradient background
        toolbar_canvas = tk.Canvas(
            toolbar_frame, height=70, bg=theme["bg"], highlightthickness=0
        )
        toolbar_canvas.pack(fill=tk.X, expand=True)

        # Create gradient
        toolbar_canvas.update_idletasks()
        width = toolbar_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 1000

        # Create gradient from top to bottom
        for i in range(70):
            # Calculate color based on position
            r1, g1, b1 = toolbar_canvas.winfo_rgb(theme["header"])
            r2, g2, b2 = toolbar_canvas.winfo_rgb(theme["bg"])

            ratio = i / 70
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            toolbar_canvas.create_line(0, i, width, i, fill=color)

        # Left side controls
        left_frame = tk.Frame(toolbar_canvas, bg=theme["header"])
        toolbar_canvas.create_window(15, 35, window=left_frame, anchor="w")

        # Add event button
        self.add_btn = ttk.Button(
            left_frame,
            text=self._("Add Event"),
            command=self.create_event,
            style="iOS.TButton",
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Today button
        self.today_btn = ttk.Button(
            left_frame,
            text=self._("Today"),
            command=self.go_to_today,
            style="Today.TButton",
        )
        self.today_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Center frame for period label
        center_frame = tk.Frame(toolbar_canvas, bg=theme["header"])
        toolbar_canvas.create_window(
            width / 2, 35, window=center_frame, anchor="center"
        )

        # Navigation buttons and period label
        self.prev_btn = ttk.Button(
            center_frame, text="<", command=self.previous_period, style="Nav.TButton"
        )
        self.prev_btn.pack(side=tk.LEFT)

        # Current period label
        self.period_var = tk.StringVar()
        self.period_label = ttk.Label(
            center_frame,
            textvariable=self.period_var,
            style="Title.TLabel",
            background=theme["header"],
        )
        self.period_label.pack(side=tk.LEFT, padx=20)

        self.next_btn = ttk.Button(
            center_frame, text=">", command=self.next_period, style="Nav.TButton"
        )
        self.next_btn.pack(side=tk.LEFT)

        # Right side controls
        right_frame = tk.Frame(toolbar_canvas, bg=theme["header"])
        toolbar_canvas.create_window(width - 15, 35, window=right_frame, anchor="e")

        # Search entry with rounded corners
        search_container = tk.Frame(
            right_frame, background=theme["header"], highlightthickness=0
        )
        search_container.pack(side=tk.RIGHT, padx=(10, 0))

        # Create a canvas for the rounded search box
        search_height = 36
        search_width = 220
        search_canvas = tk.Canvas(
            search_container,
            width=search_width,
            height=search_height,
            bg=theme["header"],
            highlightthickness=0,
        )
        search_canvas.pack()

        # Function to create rounded rectangle
        def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
            points = [
                x1 + radius,
                y1,
                x2 - radius,
                y1,
                x2,
                y1,
                x2,
                y1 + radius,
                x2,
                y2 - radius,
                x2,
                y2,
                x2 - radius,
                y2,
                x1 + radius,
                y2,
                x1,
                y2,
                x1,
                y2 - radius,
                x1,
                y1 + radius,
                x1,
                y1,
            ]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        # Draw the rounded rectangle
        search_bg_color = theme["card"]
        search_rect = create_rounded_rectangle(
            search_canvas,
            0,
            0,
            search_width,
            search_height,
            radius=18,
            fill=search_bg_color,
            outline="",
        )

        # Add search icon
        search_icon_text = "🔍"
        search_canvas.create_text(
            18,
            search_height / 2,
            text=search_icon_text,
            fill=theme["accent"],
            font=("SF Pro Display", 12),
            anchor="w",
        )

        # Add search entry
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_canvas,
            textvariable=self.search_var,
            font=("SF Pro Display", 11),
            bd=0,
            highlightthickness=0,
            bg=search_bg_color,
            fg=theme["fg"],
        )
        search_canvas.create_window(
            36,
            search_height / 2,
            window=search_entry,
            anchor="w",
            width=search_width - 50,
        )

        # Add placeholder text
        def on_entry_click(event):
            if search_entry.get() == self._("Search events..."):
                search_entry.delete(0, tk.END)
                search_entry.config(fg=theme["fg"])

        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, self._("Search events..."))
                search_entry.config(fg=theme["border"])

        search_entry.insert(0, self._("Search events..."))
        search_entry.config(fg=theme["border"])
        search_entry.bind("<FocusIn>", on_entry_click)
        search_entry.bind("<FocusOut>", on_focus_out)

        # Bind search entry to search function
        search_entry.bind("<Return>", lambda e: self.search_events())

    def register_shortcuts(self):
        """Register keyboard shortcuts"""
        self.root.bind("<Control-n>", lambda e: self.create_event())
        self.root.bind("<Control-f>", lambda e: self.search_events())
        self.root.bind("<Control-t>", lambda e: self.go_to_today())

    def create_event(self):
        """Open the event creation form"""
        EventForm(self.root, self.db_manager, self, callback=self.refresh_views)

    def edit_event(self, event_id):
        """Open the event editing form"""
        event_data = self.db_manager.get_event(event_id)
        if event_data:
            EventForm(
                self.root,
                self.db_manager,
                self,
                event_data=event_data,
                callback=self.refresh_views,
            )

    def delete_event(self, event_id):
        """Delete an event after confirmation"""
        event_data = self.db_manager.get_event(event_id)
        if event_data:
            if messagebox.askyesno(
                self._("Confirm Deletion"),
                self._("Are you sure you want to delete the event '{}'?").format(
                    event_data["title"]
                ),
            ):
                self.db_manager.delete_event(event_id)
                self.refresh_views()
                self.status_var.set(self._("Event deleted"))

    def search_events(self):
        """Search for events based on the search term"""
        search_term = self.search_var.get()
        if search_term == self._("Search events..."):
            search_term = ""

        if not search_term:
            messagebox.showinfo(self._("Search"), self._("Please enter a search term"))
            return

        # Get the current view's date range
        if self.notebook.index("current") == 0:  # Month view
            start_date, end_date = self.month_view.get_date_range()
        else:  # Week view
            start_date, end_date = self.week_view.get_date_range()

        # Search for events
        events = self.db_manager.search_events(search_term, start_date, end_date)

        # Display results
        if events:
            self.show_search_results(events)
        else:
            messagebox.showinfo(
                self._("Search Results"),
                self._("No events found matching '{}'").format(search_term),
            )

    def show_search_results(self, events):
        """Display search results in a new window"""
        theme = self.theme_manager.themes[self.theme_manager.current_theme]

        results_window = tk.Toplevel(self.root)
        results_window.title(self._("Search Results"))
        results_window.geometry("600x550")
        results_window.transient(self.root)
        results_window.grab_set()

        # Apply theme
        results_window.configure(bg=theme["bg"])

        # Create a header with gradient background
        header_frame = tk.Frame(results_window, bg=theme["bg"])
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        header_canvas = tk.Canvas(
            header_frame, height=60, bg=theme["bg"], highlightthickness=0
        )
        header_canvas.pack(fill=tk.X)

        # Create gradient
        header_canvas.update_idletasks()
        width = header_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 600

        # Create gradient from top to bottom
        for i in range(60):
            # Calculate color based on position
            r1, g1, b1 = header_canvas.winfo_rgb(theme["header"])
            r2, g2, b2 = header_canvas.winfo_rgb(theme["bg"])

            ratio = i / 60
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            header_canvas.create_line(0, i, width, i, fill=color)

        # Add title
        header_canvas.create_text(
            20,
            30,
            text=self._("Search Results"),
            fill=theme["fg"],
            font=("SF Pro Display", 18, "bold"),
            anchor="w",
        )

        # Create a frame for the events
        events_frame = ttk.Frame(results_window, style="TFrame")
        events_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create a canvas with scrollbar for the events
        canvas = tk.Canvas(events_frame, bg=theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            events_frame, orient=tk.VERTICAL, command=canvas.yview
        )

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the events
        events_list_frame = ttk.Frame(canvas, style="TFrame")
        canvas.create_window((0, 0), window=events_list_frame, anchor="nw")

        # Add events to the list
        for i, event in enumerate(sorted(events, key=lambda e: e["start_time"])):
            # Create an event card
            event_card = ttk.Frame(events_list_frame, style="Cell.TFrame", padding=15)
            event_card.pack(fill=tk.X, pady=8)

            # Event time
            start_time = datetime.fromisoformat(event["start_time"])
            end_time = datetime.fromisoformat(event["end_time"])

            time_str = f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"

            # Get color based on priority or use a color from the palette
            event_color = event.get(
                "color", self.theme_manager.get_event_color(i, event.get("priority"))
            )

            # Color indicator
            color_indicator = tk.Frame(event_card, width=6, background=event_color)
            color_indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

            # Event details
            details_frame = ttk.Frame(event_card, style="TFrame")
            details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            ttk.Label(
                details_frame,
                text=event["title"],
                style="TLabel",
                font=("SF Pro Display", 13, "bold"),
            ).pack(anchor="w")

            ttk.Label(
                details_frame, text=time_str, style="TLabel", foreground=theme["accent"]
            ).pack(anchor="w", pady=(2, 0))

            if event.get("location"):
                ttk.Label(
                    details_frame,
                    text=event["location"],
                    style="TLabel",
                    foreground=theme["fg"],
                ).pack(anchor="w", pady=(5, 0))

            if event.get("description"):
                desc_text = event["description"]
                if len(desc_text) > 100:
                    desc_text = desc_text[:97] + "..."

                ttk.Label(
                    details_frame,
                    text=desc_text,
                    style="TLabel",
                    foreground=theme["fg"],
                    wraplength=350,
                ).pack(anchor="w", pady=(5, 0))

            # Edit button
            edit_btn = ttk.Button(
                event_card,
                text=self._("Edit"),
                style="iOS.Secondary.TButton",
                command=lambda eid=event["id"]: self.edit_event(eid),
            )
            edit_btn.pack(side=tk.RIGHT, padx=5)

            # Bind double-click to edit
            event_card.bind(
                "<Double-1>", lambda e, eid=event["id"]: self.edit_event(eid)
            )

        # Update the canvas scroll region
        events_list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Add buttons at the bottom
        button_frame = ttk.Frame(results_window, style="TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Button(
            button_frame,
            text=self._("Close"),
            style="iOS.Secondary.TButton",
            command=results_window.destroy,
        ).pack(side=tk.RIGHT, padx=5)

    def import_events(self):
        """Import events from a file"""
        file_path = filedialog.askopenfilename(
            title=self._("Import Events"),
            filetypes=[
                (self._("iCalendar Files"), "*.ics"),
                (self._("CSV Files"), "*.csv"),
                (self._("All Files"), "*.*"),
            ],
        )

        if file_path:
            try:
                count = self.import_export_manager.import_events(file_path)
                if count > 0:
                    messagebox.showinfo(
                        self._("Import Successful"),
                        self._("{} events were imported successfully").format(count),
                    )
                    self.refresh_views()
                else:
                    messagebox.showinfo(
                        self._("Import"), self._("No events were imported")
                    )
            except Exception as e:
                messagebox.showerror(self._("Import Error"), str(e))

    def export_events(self):
        """Export events to a file"""
        # Get the current view's date range
        if self.notebook.index("current") == 0:  # Month view
            start_date, end_date = self.month_view.get_date_range()
        else:  # Week view
            start_date, end_date = self.week_view.get_date_range()

        # Ask if the user wants to export all events or just the current view
        export_all = messagebox.askyesno(
            self._("Export Events"),
            self._(
                "Do you want to export all events? Selecting 'No' will export only events in the current view."
            ),
        )

        if not export_all:
            events = self.db_manager.get_events_by_date_range(start_date, end_date)
        else:
            # Get all events (using a very wide date range)
            events = self.db_manager.get_events_by_date_range(
                "1900-01-01 00:00:00", "2100-12-31 23:59:59"
            )

        if not events:
            messagebox.showinfo(self._("Export"), self._("No events to export"))
            return

        # Ask for the file format
        export_format = messagebox.askquestion(
            self._("Export Format"),
            self._(
                "Do you want to export as iCalendar (.ics)? Selecting 'No' will export as CSV."
            ),
        )

        file_type = ".ics" if export_format == "yes" else ".csv"
        file_path = filedialog.asksaveasfilename(
            title=self._("Export Events"),
            defaultextension=file_type,
            filetypes=[
                (
                    (self._("iCalendar Files"), "*.ics")
                    if file_type == ".ics"
                    else (self._("CSV Files"), "*.csv")
                ),
                (self._("All Files"), "*.*"),
            ],
        )

        if file_path:
            try:
                if file_type == ".ics":
                    self.import_export_manager.export_to_ical(events, file_path)
                else:
                    self.import_export_manager.export_to_csv(events, file_path)

                messagebox.showinfo(
                    self._("Export Successful"),
                    self._("{} events were exported successfully").format(len(events)),
                )
            except Exception as e:
                messagebox.showerror(self._("Export Error"), str(e))

    def go_to_today(self):
        """Navigate to today's date in the current view"""
        if self.notebook.index("current") == 0:  # Month view
            self.month_view.go_to_today()
        else:  # Week view
            self.week_view.go_to_today()

        self.update_period_label()

    def previous_period(self):
        """Navigate to the previous period (month/week)"""
        if self.notebook.index("current") == 0:  # Month view
            self.month_view.previous_month()
        else:  # Week view
            self.week_view.previous_week()

        self.update_period_label()

    def next_period(self):
        """Navigate to the next period (month/week)"""
        if self.notebook.index("current") == 0:  # Month view
            self.month_view.next_month()
        else:  # Week view
            self.week_view.next_week()

        self.update_period_label()

    def update_period_label(self):
        """Update the period label based on the current view"""
        if self.notebook.index("current") == 0:  # Month view
            current_date = self.month_view.get_current_date()
            self.period_var.set(current_date.strftime("%B %Y"))
        else:  # Week view
            start_date, end_date = self.week_view.get_date_range()
            start_str = datetime.fromisoformat(start_date).strftime("%b %d")
            end_str = datetime.fromisoformat(end_date).strftime("%b %d, %Y")
            self.period_var.set(f"{start_str} - {end_str}")

    def on_tab_changed(self, event):
        """Handle tab change event"""
        self.update_period_label()
        self.refresh_current_view()

    def refresh_views(self):
        """Refresh all calendar views"""
        self.month_view.refresh()
        self.week_view.refresh()

    def refresh_current_view(self):
        """Refresh only the current view"""
        if self.notebook.index("current") == 0:  # Month view
            self.month_view.refresh()
        else:  # Week view
            self.week_view.refresh()

    def change_theme(self, theme_name):
        """Change the application theme"""
        self.theme_manager.set_theme(theme_name)
        self.db_manager.update_setting("theme", theme_name)

        # Refresh the UI to apply the new theme
        self.setup_ui()
        self.refresh_views()

    def change_language(self, lang_code):
        """Change the application language"""
        self.i18n.set_language(lang_code)
        self.db_manager.update_setting("language", lang_code)

        # Update UI text
        messagebox.showinfo(
            self._("Language Changed"),
            self._(
                "Please restart the application for the language change to take full effect."
            ),
        )

    def check_notifications(self):
        """Check for upcoming events and show notifications"""
        notification_time = int(
            self.db_manager.get_setting("notification_time") or "15"
        )
        self.notification_manager.check_and_notify(notification_time)

        # Schedule the next check in 1 minute
        self.root.after(60000, self.check_notifications)

    def show_about(self):
        """Show the about dialog"""
        theme = self.theme_manager.themes[self.theme_manager.current_theme]

        about_window = tk.Toplevel(self.root)
        about_window.title(self._("About Calendar & Event Manager"))
        about_window.geometry("450x500")
        about_window.transient(self.root)
        about_window.grab_set()

        # Apply theme

        # Create a canvas for the gradient background
        about_canvas = tk.Canvas(
            about_window, width=450, height=500, bg=theme["bg"], highlightthickness=0
        )
        about_canvas.pack(fill=tk.BOTH, expand=True)

        # Create a radial gradient background
        center_x, center_y = 225, 150
        radius = 300

        # Draw concentric circles with decreasing opacity
        for r in range(radius, 0, -5):
            # Calculate color based on radius
            r1, g1, b1 = about_canvas.winfo_rgb(theme["accent"])
            r2, g2, b2 = about_canvas.winfo_rgb(theme["bg"])

            ratio = r / radius
            r_color = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g_color = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b_color = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r_color:02x}{g_color:02x}{b_color:02x}"

            about_canvas.create_oval(
                center_x - r,
                center_y - r,
                center_x + r,
                center_y + r,
                outline=color,
                width=5,
                fill="",
            )

        # App icon (using emoji as placeholder)
        about_canvas.create_text(
            225, 120, text="📅", fill=theme["accent"], font=("SF Pro Display", 64)
        )

        about_canvas.create_text(
            225,
            200,
            text="Calendar & Event Manager",
            fill=theme["fg"],
            font=("SF Pro Display", 18, "bold"),
        )

        about_canvas.create_text(
            225,
            230,
            text="Version 1.0.0",
            fill=theme["fg"],
            font=("SF Pro Display", 11),
        )

        about_canvas.create_text(
            225,
            260,
            text=self._("A feature-rich desktop calendar application"),
            fill=theme["fg"],
            font=("SF Pro Display", 12),
        )

        features_text = self._(
            "• Modern blue-themed interface\n• Multiple calendar views\n• Event management with priorities\n• Import/Export to iCal and CSV\n• Notifications for upcoming events\n• Light and dark themes"
        )

        about_canvas.create_text(
            225,
            330,
            text=features_text,
            fill=theme["fg"],
            font=("SF Pro Display", 12),
            justify=tk.CENTER,
        )

        about_canvas.create_text(
            225, 400, text="© 2023", fill=theme["fg"], font=("SF Pro Display", 11)
        )

        # Close button
        close_btn = ttk.Button(
            about_canvas,
            text=self._("Close"),
            style="iOS.TButton",
            command=about_window.destroy,
        )
        about_canvas.create_window(225, 450, window=close_btn)
