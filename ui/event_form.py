import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from datetime import datetime, timedelta


class EventForm:
    """Form for creating and editing events"""

    def __init__(self, parent, db_manager, app, event_data=None, callback=None):
        """Initialize the event form"""
        self.parent = parent
        self.db_manager = db_manager
        self.app = app
        self._ = app.i18n.gettext
        self.event_data = event_data or {}
        self.callback = callback
        self.theme = self.app.theme_manager.themes[self.app.theme_manager.current_theme]

        # Create the form window
        self.window = tk.Toplevel(parent)
        self.window.title(
            self._("Add Event")
            if not event_data or "id" not in event_data
            else self._("Edit Event")
        )
        self.window.geometry("650x650")
        self.window.transient(parent)
        self.window.grab_set()

        # Apply theme
        self.window.configure(bg=self.theme["bg"])

        # Make the window responsive
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Create the form
        self.create_form()

    def create_form(self):
        """Create the event form"""
        # Main frame
        main_frame = ttk.Frame(self.window, style="TFrame", padding=25)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)

        # Create a header with gradient background
        header_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 25))

        header_canvas = tk.Canvas(
            header_frame, height=60, bg=self.theme["bg"], highlightthickness=0
        )
        header_canvas.pack(fill=tk.X)

        # Create gradient
        header_canvas.update_idletasks()
        width = header_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 650

        # Create gradient from left to right
        for i in range(width):
            # Calculate color based on position
            r1, g1, b1 = header_canvas.winfo_rgb(self.theme["bg"])
            r2, g2, b2 = header_canvas.winfo_rgb(self.theme["accent"])

            # Adjust the gradient to be subtle
            ratio = i / width * 0.2  # Only go 20% toward the accent color
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            header_canvas.create_line(i, 0, i, 60, fill=color)

        # Add title
        header_text = (
            self._("Add Event")
            if not self.event_data or "id" not in self.event_data
            else self._("Edit Event")
        )
        header_canvas.create_text(
            20,
            30,
            text=header_text,
            fill=self.theme["fg"],
            font=("SF Pro Display", 18, "bold"),
            anchor="w",
        )

        # Title
        ttk.Label(
            main_frame,
            text=self._("Title:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))
        self.title_var = tk.StringVar(value=self.event_data.get("title", ""))
        title_entry = ttk.Entry(
            main_frame, textvariable=self.title_var, font=("SF Pro Display", 13)
        )
        title_entry.grid(row=1, column=1, sticky="ew", pady=(0, 15))

        # Description
        ttk.Label(
            main_frame,
            text=self._("Description:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=2, column=0, sticky="nw", pady=(0, 15))

        # Create a frame for the description text area with a border
        desc_frame = ttk.Frame(main_frame, style="Cell.TFrame")
        desc_frame.grid(row=2, column=1, sticky="ew", pady=(0, 15))
        desc_frame.columnconfigure(0, weight=1)

        self.description_text = tk.Text(
            desc_frame,
            height=4,
            width=40,
            font=("SF Pro Display", 12),
            bg=self.theme["card"],
            fg=self.theme["fg"],
            bd=0,
            padx=8,
            pady=8,
        )
        self.description_text.grid(row=0, column=0, sticky="ew", padx=1, pady=1)

        if "description" in self.event_data:
            self.description_text.insert("1.0", self.event_data["description"])

        # Start time
        ttk.Label(
            main_frame,
            text=self._("Start Time:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=(0, 15))
        start_frame = ttk.Frame(main_frame, style="TFrame")
        start_frame.grid(row=3, column=1, sticky="ew", pady=(0, 15))

        # Parse start time or use current time
        if "start_time" in self.event_data:
            start_time = datetime.fromisoformat(self.event_data["start_time"])
        else:
            start_time = datetime.now().replace(minute=0, second=0) + timedelta(hours=1)

        # Date picker for start date
        self.start_date_var = tk.StringVar(value=start_time.strftime("%Y-%m-%d"))
        ttk.Label(start_frame, text=self._("Date:"), style="TLabel").pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # Create a frame for the date entry with a border
        start_date_frame = ttk.Frame(start_frame, style="Cell.TFrame")
        start_date_frame.pack(side=tk.LEFT, padx=(0, 15))

        self.start_date_entry = ttk.Entry(
            start_date_frame,
            textvariable=self.start_date_var,
            width=12,
            font=("SF Pro Display", 12),
        )
        self.start_date_entry.pack(side=tk.LEFT, padx=1, pady=1)

        ttk.Button(
            start_frame,
            text="...",
            width=3,
            style="iOS.Secondary.TButton",
            command=lambda: self.show_date_picker(self.start_date_entry),
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Time picker for start time
        ttk.Label(start_frame, text=self._("Time:"), style="TLabel").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.start_hour_var = tk.StringVar(value=start_time.strftime("%H"))
        self.start_minute_var = tk.StringVar(value=start_time.strftime("%M"))

        # Create frames for the time entries with borders
        start_hour_frame = ttk.Frame(start_frame, style="Cell.TFrame")
        start_hour_frame.pack(side=tk.LEFT)

        # Hour combobox
        hour_values = [f"{h:02d}" for h in range(24)]
        ttk.Combobox(
            start_hour_frame,
            textvariable=self.start_hour_var,
            values=hour_values,
            width=3,
            font=("SF Pro Display", 12),
        ).pack(side=tk.LEFT, padx=1, pady=1)

        ttk.Label(
            start_frame, text=":", style="TLabel", font=("SF Pro Display", 12, "bold")
        ).pack(side=tk.LEFT)

        start_minute_frame = ttk.Frame(start_frame, style="Cell.TFrame")
        start_minute_frame.pack(side=tk.LEFT)

        # Minute combobox
        minute_values = [f"{m:02d}" for m in range(0, 60, 5)]
        ttk.Combobox(
            start_minute_frame,
            textvariable=self.start_minute_var,
            values=minute_values,
            width=3,
            font=("SF Pro Display", 12),
        ).pack(side=tk.LEFT, padx=1, pady=1)

        # End time
        ttk.Label(
            main_frame,
            text=self._("End Time:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=4, column=0, sticky="w", pady=(0, 15))
        end_frame = ttk.Frame(main_frame, style="TFrame")
        end_frame.grid(row=4, column=1, sticky="ew", pady=(0, 15))

        # Parse end time or use current time + 1 hour
        if "end_time" in self.event_data:
            end_time = datetime.fromisoformat(self.event_data["end_time"])
        else:
            end_time = start_time + timedelta(hours=1)

        # Date picker for end date
        self.end_date_var = tk.StringVar(value=end_time.strftime("%Y-%m-%d"))
        ttk.Label(end_frame, text=self._("Date:"), style="TLabel").pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # Create a frame for the date entry with a border
        end_date_frame = ttk.Frame(end_frame, style="Cell.TFrame")
        end_date_frame.pack(side=tk.LEFT, padx=(0, 15))

        self.end_date_entry = ttk.Entry(
            end_date_frame,
            textvariable=self.end_date_var,
            width=12,
            font=("SF Pro Display", 12),
        )
        self.end_date_entry.pack(side=tk.LEFT, padx=1, pady=1)

        ttk.Button(
            end_frame,
            text="...",
            width=3,
            style="iOS.Secondary.TButton",
            command=lambda: self.show_date_picker(self.end_date_entry),
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Time picker for end time
        ttk.Label(end_frame, text=self._("Time:"), style="TLabel").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.end_hour_var = tk.StringVar(value=end_time.strftime("%H"))
        self.end_minute_var = tk.StringVar(value=end_time.strftime("%M"))

        # Create frames for the time entries with borders
        end_hour_frame = ttk.Frame(end_frame, style="Cell.TFrame")
        end_hour_frame.pack(side=tk.LEFT)

        # Hour combobox
        ttk.Combobox(
            end_hour_frame,
            textvariable=self.end_hour_var,
            values=hour_values,
            width=3,
            font=("SF Pro Display", 12),
        ).pack(side=tk.LEFT, padx=1, pady=1)

        ttk.Label(
            end_frame, text=":", style="TLabel", font=("SF Pro Display", 12, "bold")
        ).pack(side=tk.LEFT)

        end_minute_frame = ttk.Frame(end_frame, style="Cell.TFrame")
        end_minute_frame.pack(side=tk.LEFT)

        # Minute combobox
        ttk.Combobox(
            end_minute_frame,
            textvariable=self.end_minute_var,
            values=minute_values,
            width=3,
            font=("SF Pro Display", 12),
        ).pack(side=tk.LEFT, padx=1, pady=1)

        # Location
        ttk.Label(
            main_frame,
            text=self._("Location:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=5, column=0, sticky="w", pady=(0, 15))

        # Create a frame for the location entry with a border
        location_frame = ttk.Frame(main_frame, style="Cell.TFrame")
        location_frame.grid(row=5, column=1, sticky="ew", pady=(0, 15))

        self.location_var = tk.StringVar(value=self.event_data.get("location", ""))
        ttk.Entry(
            location_frame, textvariable=self.location_var, font=("SF Pro Display", 12)
        ).pack(fill=tk.X, padx=1, pady=1)

        # Priority
        ttk.Label(
            main_frame,
            text=self._("Priority:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=6, column=0, sticky="w", pady=(0, 15))
        priority_frame = ttk.Frame(main_frame, style="TFrame")
        priority_frame.grid(row=6, column=1, sticky="ew", pady=(0, 15))

        self.priority_var = tk.StringVar(
            value=self.event_data.get("priority", "medium")
        )

        # Create priority buttons with blue-styled appearance
        low_color = self.theme["success"]
        medium_color = self.theme["warning"]
        high_color = self.theme["danger"]

        # Low priority button
        low_frame = tk.Frame(priority_frame, bg=self.theme["bg"])
        low_frame.pack(side=tk.LEFT, padx=(0, 10))

        low_canvas = tk.Canvas(
            low_frame, width=90, height=36, bg=self.theme["bg"], highlightthickness=0
        )
        low_canvas.pack()

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

        # Draw the low priority button
        low_fill = (
            low_color if self.priority_var.get() == "low" else self.theme["button"]
        )
        low_text_color = (
            "white" if self.priority_var.get() == "low" else self.theme["fg"]
        )

        low_rect = create_rounded_rectangle(
            low_canvas, 0, 0, 90, 36, radius=18, fill=low_fill, outline=""
        )

        low_text = low_canvas.create_text(
            45,
            18,
            text=self._("Low"),
            fill=low_text_color,
            font=("SF Pro Display", 12, "bold"),
        )

        # Bind click event
        def set_low_priority(event):
            self.priority_var.set("low")
            low_canvas.itemconfig(low_rect, fill=low_color)
            low_canvas.itemconfig(low_text, fill="white")
            medium_canvas.itemconfig(medium_rect, fill=self.theme["button"])
            medium_canvas.itemconfig(medium_text, fill=self.theme["fg"])
            high_canvas.itemconfig(high_rect, fill=self.theme["button"])
            high_canvas.itemconfig(high_text, fill=self.theme["fg"])

        low_canvas.bind("<Button-1>", set_low_priority)

        # Medium priority button
        medium_frame = tk.Frame(priority_frame, bg=self.theme["bg"])
        medium_frame.pack(side=tk.LEFT, padx=(0, 10))

        medium_canvas = tk.Canvas(
            medium_frame, width=90, height=36, bg=self.theme["bg"], highlightthickness=0
        )
        medium_canvas.pack()

        # Draw the medium priority button
        medium_fill = (
            medium_color
            if self.priority_var.get() == "medium"
            else self.theme["button"]
        )
        medium_text_color = (
            "white" if self.priority_var.get() == "medium" else self.theme["fg"]
        )

        medium_rect = create_rounded_rectangle(
            medium_canvas, 0, 0, 90, 36, radius=18, fill=medium_fill, outline=""
        )

        medium_text = medium_canvas.create_text(
            45,
            18,
            text=self._("Medium"),
            fill=medium_text_color,
            font=("SF Pro Display", 12, "bold"),
        )

        # Bind click event
        def set_medium_priority(event):
            self.priority_var.set("medium")
            low_canvas.itemconfig(low_rect, fill=self.theme["button"])
            low_canvas.itemconfig(low_text, fill=self.theme["fg"])
            medium_canvas.itemconfig(medium_rect, fill=medium_color)
            medium_canvas.itemconfig(medium_text, fill="white")
            high_canvas.itemconfig(high_rect, fill=self.theme["button"])
            high_canvas.itemconfig(high_text, fill=self.theme["fg"])

        medium_canvas.bind("<Button-1>", set_medium_priority)

        # High priority button
        high_frame = tk.Frame(priority_frame, bg=self.theme["bg"])
        high_frame.pack(side=tk.LEFT)

        high_canvas = tk.Canvas(
            high_frame, width=90, height=36, bg=self.theme["bg"], highlightthickness=0
        )
        high_canvas.pack()

        # Draw the high priority button
        high_fill = (
            high_color if self.priority_var.get() == "high" else self.theme["button"]
        )
        high_text_color = (
            "white" if self.priority_var.get() == "high" else self.theme["fg"]
        )

        high_rect = create_rounded_rectangle(
            high_canvas, 0, 0, 90, 36, radius=18, fill=high_fill, outline=""
        )

        high_text = high_canvas.create_text(
            45,
            18,
            text=self._("High"),
            fill=high_text_color,
            font=("SF Pro Display", 12, "bold"),
        )

        # Bind click event
        def set_high_priority(event):
            self.priority_var.set("high")
            low_canvas.itemconfig(low_rect, fill=self.theme["button"])
            low_canvas.itemconfig(low_text, fill=self.theme["fg"])
            medium_canvas.itemconfig(medium_rect, fill=self.theme["button"])
            medium_canvas.itemconfig(medium_text, fill=self.theme["fg"])
            high_canvas.itemconfig(high_rect, fill=high_color)
            high_canvas.itemconfig(high_text, fill="white")

        high_canvas.bind("<Button-1>", set_high_priority)

        # Color
        ttk.Label(
            main_frame,
            text=self._("Color:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=7, column=0, sticky="w", pady=(0, 15))
        color_frame = ttk.Frame(main_frame, style="TFrame")
        color_frame.grid(row=7, column=1, sticky="ew", pady=(0, 15))

        self.color_var = tk.StringVar(
            value=self.event_data.get("color", self.theme["accent"])
        )

        # Create a color preview with rounded corners
        color_preview_frame = tk.Frame(color_frame, bg=self.theme["bg"])
        color_preview_frame.pack(side=tk.LEFT, padx=(0, 15))

        color_preview_canvas = tk.Canvas(
            color_preview_frame,
            width=36,
            height=36,
            bg=self.theme["bg"],
            highlightthickness=0,
        )
        color_preview_canvas.pack()

        # Draw the color preview
        self.color_preview_rect = create_rounded_rectangle(
            color_preview_canvas,
            0,
            0,
            36,
            36,
            radius=18,
            fill=self.color_var.get(),
            outline="",
        )
        # Store reference to canvas
        self.color_preview_canvas = color_preview_canvas

        # Choose color button
        ttk.Button(
            color_frame,
            text=self._("Choose Color"),
            style="iOS.Secondary.TButton",
            command=self.choose_color,
        ).pack(side=tk.LEFT)

        # Recurring event
        ttk.Label(
            main_frame,
            text=self._("Recurring:"),
            style="TLabel",
            font=("SF Pro Display", 13, "bold"),
        ).grid(row=8, column=0, sticky="w", pady=(0, 15))
        recurring_frame = ttk.Frame(main_frame, style="TFrame")
        recurring_frame.grid(row=8, column=1, sticky="ew", pady=(0, 15))

        self.is_recurring_var = tk.BooleanVar(
            value=bool(self.event_data.get("is_recurring", False))
        )

        # Create a custom switch for recurring events
        switch_frame = tk.Frame(recurring_frame, bg=self.theme["bg"])
        switch_frame.pack(side=tk.LEFT, padx=(0, 15))

        switch_width = 60
        switch_height = 36
        switch_canvas = tk.Canvas(
            switch_frame,
            width=switch_width,
            height=switch_height,
            bg=self.theme["bg"],
            highlightthickness=0,
        )
        switch_canvas.pack()

        # Draw the switch background
        switch_bg_color = (
            self.theme["success"]
            if self.is_recurring_var.get()
            else self.theme["button"]
        )
        self.switch_bg = create_rounded_rectangle(
            switch_canvas,
            0,
            0,
            switch_width,
            switch_height,
            radius=18,
            fill=switch_bg_color,
            outline="",
        )

        # Draw the switch handle
        handle_pos = switch_width - 24 if self.is_recurring_var.get() else 6
        self.switch_handle = switch_canvas.create_oval(
            handle_pos, 6, handle_pos + 24, 30, fill="white", outline=""
        )

        # Bind click event
        def toggle_recurring(event):
            self.is_recurring_var.set(not self.is_recurring_var.get())
            if self.is_recurring_var.get():
                switch_canvas.itemconfig(self.switch_bg, fill=self.theme["success"])
                switch_canvas.coords(
                    self.switch_handle, switch_width - 30, 6, switch_width - 6, 30
                )
                self.recurring_options_frame.grid()
            else:
                switch_canvas.itemconfig(self.switch_bg, fill=self.theme["button"])
                switch_canvas.coords(self.switch_handle, 6, 6, 30, 30)
                self.recurring_options_frame.grid_remove()

        switch_canvas.bind("<Button-1>", toggle_recurring)

        ttk.Label(
            recurring_frame,
            text=self._("This is a recurring event"),
            style="TLabel",
            font=("SF Pro Display", 12),
        ).pack(side=tk.LEFT)

        # Recurring options frame
        self.recurring_options_frame = ttk.Frame(main_frame, style="TFrame", padding=15)
        self.recurring_options_frame.grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # Recurrence type
        ttk.Label(
            self.recurring_options_frame,
            text=self._("Repeat:"),
            style="TLabel",
            font=("SF Pro Display", 12, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.recurrence_type_var = tk.StringVar(
            value=self.event_data.get("recurrence_type", "daily")
        )
        recurrence_types = [
            ("daily", self._("Daily")),
            ("weekly", self._("Weekly")),
            ("monthly", self._("Monthly")),
            ("yearly", self._("Yearly")),
        ]

        recurrence_type_frame = ttk.Frame(self.recurring_options_frame, style="TFrame")
        recurrence_type_frame.grid(row=0, column=1, sticky="ew", pady=5)

        # Create custom radio buttons for recurrence type
        for i, (value, text) in enumerate(recurrence_types):
            radio_frame = tk.Frame(recurrence_type_frame, bg=self.theme["bg"])
            radio_frame.pack(side=tk.LEFT, padx=(0, 10))

            radio_canvas = tk.Canvas(
                radio_frame,
                width=90,
                height=36,
                bg=self.theme["bg"],
                highlightthickness=0,
            )
            radio_canvas.pack()

            # Draw the radio button
            is_selected = self.recurrence_type_var.get() == value
            radio_fill = self.theme["accent"] if is_selected else self.theme["button"]
            radio_text_color = "white" if is_selected else self.theme["fg"]

            radio_rect = create_rounded_rectangle(
                radio_canvas, 0, 0, 90, 36, radius=18, fill=radio_fill, outline=""
            )

            radio_text = radio_canvas.create_text(
                45,
                18,
                text=text,
                fill=radio_text_color,
                font=("SF Pro Display", 12, "bold"),
            )

            # Store references to canvas items
            radio_canvas.rect = radio_rect
            radio_canvas.text = radio_text
            radio_canvas.value = value

            # Bind click event
            def set_recurrence_type(event):
                canvas = event.widget
                self.recurrence_type_var.set(canvas.value)

                # Update all radio buttons
                for child in recurrence_type_frame.winfo_children():
                    child_canvas = child.winfo_children()[0]
                    is_selected = self.recurrence_type_var.get() == child_canvas.value
                    fill_color = (
                        self.theme["accent"] if is_selected else self.theme["button"]
                    )
                    text_color = "white" if is_selected else self.theme["fg"]

                    child_canvas.itemconfig(child_canvas.rect, fill=fill_color)
                    child_canvas.itemconfig(child_canvas.text, fill=text_color)

            radio_canvas.bind("<Button-1>", set_recurrence_type)

        # End recurrence
        ttk.Label(
            self.recurring_options_frame,
            text=self._("End Recurrence:"),
            style="TLabel",
            font=("SF Pro Display", 12, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=5)

        end_recurrence_frame = ttk.Frame(self.recurring_options_frame, style="TFrame")
        end_recurrence_frame.grid(row=1, column=1, sticky="ew", pady=5)

        # Default end date is 1 month from start
        default_end_date = start_time + timedelta(days=30)
        if (
            "recurrence_end_date" in self.event_data
            and self.event_data["recurrence_end_date"]
        ):
            recurrence_end_date = datetime.fromisoformat(
                self.event_data["recurrence_end_date"]
            )
            self.recurrence_end_date_var = tk.StringVar(
                value=recurrence_end_date.strftime("%Y-%m-%d")
            )
        else:
            self.recurrence_end_date_var = tk.StringVar(
                value=default_end_date.strftime("%Y-%m-%d")
            )

        ttk.Label(end_recurrence_frame, text=self._("Date:"), style="TLabel").pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # Create a frame for the recurrence end date entry with a border
        recurrence_end_date_frame = ttk.Frame(end_recurrence_frame, style="Cell.TFrame")
        recurrence_end_date_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.recurrence_end_date_entry = ttk.Entry(
            recurrence_end_date_frame,
            textvariable=self.recurrence_end_date_var,
            width=12,
            font=("SF Pro Display", 12),
        )
        self.recurrence_end_date_entry.pack(side=tk.LEFT, padx=1, pady=1)

        ttk.Button(
            end_recurrence_frame,
            text="...",
            width=3,
            style="iOS.Secondary.TButton",
            command=lambda: self.show_date_picker(self.recurrence_end_date_entry),
        ).pack(side=tk.LEFT)

        # Show/hide recurring options based on checkbox
        if not self.is_recurring_var.get():
            self.recurring_options_frame.grid_remove()

        # Buttons
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(20, 0))

        # Add delete button if editing an existing event
        if self.event_data and "id" in self.event_data:
            ttk.Button(
                button_frame,
                text=self._("Delete"),
                style="iOS.Secondary.TButton",
                command=self.delete_event,
            ).pack(side=tk.LEFT, padx=5)

            # Add history button
            ttk.Button(
                button_frame,
                text=self._("History"),
                style="iOS.Secondary.TButton",
                command=self.show_event_history,
            ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text=self._("Cancel"),
            style="iOS.Secondary.TButton",
            command=self.window.destroy,
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text=self._("Save"),
            style="iOS.TButton",
            command=self.save_event,
        ).pack(side=tk.RIGHT, padx=5)

    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(initialcolor=self.color_var.get())
        if color[1]:  # color is a tuple (RGB, hex)
            self.color_var.set(color[1])
            self.color_preview_canvas.itemconfig(self.color_preview_rect, fill=color[1])

    def show_date_picker(self, entry_widget):
        """Show a date picker dialog"""
        # Get the current date from the entry
        try:
            current_date = datetime.strptime(entry_widget.get(), "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()

        # Create a toplevel window for the date picker
        date_window = tk.Toplevel(self.window)
        date_window.title(self._("Select Date"))
        date_window.geometry("400x450")
        date_window.transient(self.window)
        date_window.grab_set()

        # Apply theme
        date_window.configure(bg=self.theme["bg"])

        # Create the date picker UI
        date_frame = ttk.Frame(date_window, style="TFrame", padding=20)
        date_frame.pack(fill=tk.BOTH, expand=True)

        # Header with gradient background
        header_frame = tk.Frame(date_frame, bg=self.theme["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        header_canvas = tk.Canvas(
            header_frame, height=50, bg=self.theme["bg"], highlightthickness=0
        )
        header_canvas.pack(fill=tk.X)

        # Create gradient
        header_canvas.update_idletasks()
        width = header_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 400

        # Create gradient from left to right
        for i in range(width):
            # Calculate color based on position
            r1, g1, b1 = header_canvas.winfo_rgb(self.theme["bg"])
            r2, g2, b2 = header_canvas.winfo_rgb(self.theme["accent"])

            # Adjust the gradient to be subtle
            ratio = i / width * 0.2  # Only go 20% toward the accent color
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            header_canvas.create_line(i, 0, i, 50, fill=color)

        # Add title
        header_canvas.create_text(
            20,
            25,
            text=self._("Select Date"),
            fill=self.theme["fg"],
            font=("SF Pro Display", 16, "bold"),
            anchor="w",
        )

        # Year and month selection
        year_month_frame = ttk.Frame(date_frame, style="TFrame")
        year_month_frame.pack(fill=tk.X, pady=(0, 15))

        # Previous month button
        def prev_month():
            month = self.month_var.get()
            year = self.year_var.get()
            if month == 1:
                self.month_var.set(12)
                self.year_var.set(year - 1)
            else:
                self.month_var.set(month - 1)

        prev_month_btn = ttk.Button(
            year_month_frame, text="<", style="Nav.TButton", command=prev_month
        )
        prev_month_btn.pack(side=tk.LEFT)

        # Month selection
        import calendar

        month_names = [calendar.month_name[i] for i in range(1, 13)]
        self.month_var = tk.IntVar(value=current_date.month)

        month_label = ttk.Label(
            year_month_frame,
            text=month_names[current_date.month - 1],
            style="Subtitle.TLabel",
        )
        month_label.pack(side=tk.LEFT, padx=10)

        # Update month label when month changes
        def update_month_label(*args):
            month = self.month_var.get()
            month_label.config(text=month_names[month - 1])
            self.update_calendar()

        self.month_var.trace_add("write", update_month_label)

        # Year selection
        self.year_var = tk.IntVar(value=current_date.year)

        year_label = ttk.Label(
            year_month_frame, text=str(current_date.year), style="Subtitle.TLabel"
        )
        year_label.pack(side=tk.LEFT, padx=10)

        # Update year label when year changes
        def update_year_label(*args):
            year = self.year_var.get()
            year_label.config(text=str(year))
            self.update_calendar()

        self.year_var.trace_add("write", update_year_label)

        # Next month button
        def next_month():
            month = self.month_var.get()
            year = self.year_var.get()
            if month == 12:
                self.month_var.set(1)
                self.year_var.set(year + 1)
            else:
                self.month_var.set(month + 1)

        next_month_btn = ttk.Button(
            year_month_frame, text=">", style="Nav.TButton", command=next_month
        )
        next_month_btn.pack(side=tk.LEFT)

        # Create calendar grid
        self.cal_frame = ttk.Frame(date_frame, style="TFrame")
        self.cal_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Initial calendar display
        self.update_calendar(date_window, entry_widget)

        # Buttons
        button_frame = ttk.Frame(date_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(
            button_frame,
            text=self._("Today"),
            style="Today.TButton",
            command=lambda: self.select_date(
                datetime.now().year,
                datetime.now().month,
                datetime.now().day,
                date_window,
                entry_widget,
            ),
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text=self._("Cancel"),
            style="iOS.Secondary.TButton",
            command=date_window.destroy,
        ).pack(side=tk.RIGHT, padx=5)

    def update_calendar(self, date_window=None, entry_widget=None):
        """Update the calendar grid"""
        # Clear the calendar frame
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        # Get the selected year and month
        year = self.year_var.get()
        month = self.month_var.get()

        # Create calendar object
        import calendar

        cal = calendar.Calendar(firstweekday=0)

        # Create day headers
        days = [
            self._("Mon"),
            self._("Tue"),
            self._("Wed"),
            self._("Thu"),
            self._("Fri"),
            self._("Sat"),
            self._("Sun"),
        ]

        for i, day in enumerate(days):
            ttk.Label(
                self.cal_frame, text=day, style="DayHeader.TLabel", anchor="center"
            ).grid(row=0, column=i, padx=2, pady=5, sticky="nsew")
            self.cal_frame.columnconfigure(i, weight=1)

        # Get the calendar for the selected month
        month_cal = cal.monthdayscalendar(year, month)

        # Get today's date
        today = datetime.now().date()

        # Create day buttons
        for week_idx, week in enumerate(month_cal):
            for day_idx, day in enumerate(week):
                if day != 0:
                    # Check if this is today
                    is_today = (
                        year == today.year and month == today.month and day == today.day
                    )

                    # Create a frame for the day button
                    day_frame = tk.Frame(self.cal_frame, bg=self.theme["bg"])
                    day_frame.grid(
                        row=week_idx + 1, column=day_idx, padx=2, pady=2, sticky="nsew"
                    )
                    self.cal_frame.rowconfigure(week_idx + 1, weight=1)

                    # Create a canvas for the day button
                    day_canvas = tk.Canvas(
                        day_frame,
                        width=45,
                        height=45,
                        bg=self.theme["bg"],
                        highlightthickness=0,
                    )
                    day_canvas.pack(expand=True)

                    # Draw the day button
                    if is_today:
                        # Draw a filled circle for today
                        day_canvas.create_oval(
                            8, 8, 38, 38, fill=self.theme["accent"], outline=""
                        )
                        day_canvas.create_text(
                            23,
                            23,
                            text=str(day),
                            fill="white",
                            font=("SF Pro Display", 13, "bold"),
                        )
                    else:
                        # Draw just the text for other days
                        day_canvas.create_text(
                            23,
                            23,
                            text=str(day),
                            fill=self.theme["fg"],
                            font=("SF Pro Display", 13),
                        )

                    # Add hover effect
                    def on_enter(e, canvas=day_canvas, is_today=is_today):
                        if not is_today:
                            canvas.create_oval(
                                8,
                                8,
                                38,
                                38,
                                fill=self.theme["button"],
                                outline="",
                                tags="hover",
                            )
                            canvas.tag_lower("hover")

                    def on_leave(e, canvas=day_canvas, is_today=is_today):
                        if not is_today:
                            canvas.delete("hover")

                    day_canvas.bind("<Enter>", on_enter)
                    day_canvas.bind("<Leave>", on_leave)

                    # Bind click event
                    day_canvas.bind(
                        "<Button-1>",
                        lambda e, y=year, m=month, d=day: self.select_date(
                            y, m, d, date_window, entry_widget
                        ),
                    )

    def select_date(self, year, month, day, date_window, entry_widget):
        """Select a date and close the picker"""
        selected_date = datetime(year, month, day)
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, selected_date.strftime("%Y-%m-%d"))
        date_window.destroy()

    def save_event(self):
        """Save the event data"""
        # Validate required fields
        if not self.title_var.get().strip():
            messagebox.showerror(self._("Error"), self._("Title is required"))
            return

        try:
            # Parse start and end times
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            start_time = datetime(
                start_date.year,
                start_date.month,
                start_date.day,
                int(self.start_hour_var.get()),
                int(self.start_minute_var.get()),
            )

            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            end_time = datetime(
                end_date.year,
                end_date.month,
                end_date.day,
                int(self.end_hour_var.get()),
                int(self.end_minute_var.get()),
            )

            # Validate that end time is after start time
            if end_time <= start_time:
                messagebox.showerror(
                    self._("Error"), self._("End time must be after start time")
                )
                return

            # Get recurrence end date if applicable
            recurrence_end_date = None
            if self.is_recurring_var.get():
                recurrence_end_date = datetime.strptime(
                    self.recurrence_end_date_var.get(), "%Y-%m-%d"
                ).strftime("%Y-%m-%d 23:59:59")

            # Prepare event data
            event_data = {
                "title": self.title_var.get().strip(),
                "description": self.description_text.get("1.0", tk.END).strip(),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "location": self.location_var.get().strip(),
                "priority": self.priority_var.get(),
                "color": self.color_var.get(),
                "is_recurring": self.is_recurring_var.get(),
                "recurrence_type": (
                    self.recurrence_type_var.get()
                    if self.is_recurring_var.get()
                    else None
                ),
                "recurrence_end_date": recurrence_end_date,
            }

            # Save to database
            if self.event_data and "id" in self.event_data:
                # Update existing event
                self.db_manager.update_event(self.event_data["id"], event_data)
                messagebox.showinfo(
                    self._("Success"), self._("Event updated successfully")
                )
            else:
                # Create new event
                self.db_manager.add_event(event_data)
                messagebox.showinfo(
                    self._("Success"), self._("Event created successfully")
                )

            # Call the callback function if provided
            if self.callback:
                self.callback()

            # Close the window
            self.window.destroy()

        except ValueError as e:
            messagebox.showerror(self._("Error"), str(e))

    def delete_event(self):
        """Delete the current event"""
        if "id" in self.event_data:
            if messagebox.askyesno(
                self._("Confirm Deletion"),
                self._("Are you sure you want to delete this event?"),
            ):
                self.db_manager.delete_event(self.event_data["id"])

                # Call the callback function if provided
                if self.callback:
                    self.callback()

                # Close the window
                self.window.destroy()

    def show_event_history(self):
        """Show the history of changes for this event"""
        if "id" not in self.event_data:
            return

        # Get event history
        history = self.db_manager.get_event_history(self.event_data["id"])

        if not history:
            messagebox.showinfo(
                self._("Event History"), self._("No history found for this event")
            )
            return

        # Create history window
        history_window = tk.Toplevel(self.window)
        history_window.title(self._("Event History"))
        history_window.geometry("550x450")
        history_window.transient(self.window)
        history_window.grab_set()

        # Apply theme
        history_window.configure(bg=self.theme["bg"])

        # Create a header with gradient background
        header_frame = tk.Frame(history_window, bg=self.theme["bg"])
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        header_canvas = tk.Canvas(
            header_frame, height=60, bg=self.theme["bg"], highlightthickness=0
        )
        header_canvas.pack(fill=tk.X)

        # Create gradient
        header_canvas.update_idletasks()
        width = header_canvas.winfo_width()
        if width < 10:  # If not yet rendered, use a default
            width = 550

        # Create gradient from left to right
        for i in range(width):
            # Calculate color based on position
            r1, g1, b1 = header_canvas.winfo_rgb(self.theme["bg"])
            r2, g2, b2 = header_canvas.winfo_rgb(self.theme["accent"])

            # Adjust the gradient to be subtle
            ratio = i / width * 0.2  # Only go 20% toward the accent color
            r = int(r1 * (1 - ratio) + r2 * ratio) >> 8
            g = int(g1 * (1 - ratio) + g2 * ratio) >> 8
            b = int(b1 * (1 - ratio) + b2 * ratio) >> 8

            color = f"#{r:02x}{g:02x}{b:02x}"
            header_canvas.create_line(i, 0, i, 60, fill=color)

        # Add title
        header_canvas.create_text(
            20,
            30,
            text=self._("Event History"),
            fill=self.theme["fg"],
            font=("SF Pro Display", 18, "bold"),
            anchor="w",
        )

        # Create a frame for the history entries
        history_frame = ttk.Frame(history_window, style="TFrame")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create a canvas with scrollbar for the history entries
        canvas = tk.Canvas(history_frame, bg=self.theme["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            history_frame, orient=tk.VERTICAL, command=canvas.yview
        )

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the history entries
        history_list_frame = ttk.Frame(canvas, style="TFrame")
        canvas.create_window((0, 0), window=history_list_frame, anchor="nw")

        # Add history entries to the list
        for entry in history:
            # Create a history entry card
            entry_card = ttk.Frame(history_list_frame, style="Cell.TFrame", padding=15)
            entry_card.pack(fill=tk.X, pady=8)

            # Entry timestamp
            timestamp = datetime.fromisoformat(entry["timestamp"])

            # Entry details
            details_frame = ttk.Frame(entry_card, style="TFrame")
            details_frame.pack(fill=tk.BOTH, expand=True)

            # Action with appropriate color
            action_color = self.theme["fg"]
            if entry["action"] == "create":
                action_color = self.theme["success"]
            elif entry["action"] == "update":
                action_color = self.theme["warning"]
            elif entry["action"] == "delete":
                action_color = self.theme["danger"]

            ttk.Label(
                details_frame,
                text=entry["action"].capitalize(),
                style="TLabel",
                font=("SF Pro Display", 13, "bold"),
                foreground=action_color,
            ).pack(anchor="w")

            ttk.Label(
                details_frame,
                text=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                style="TLabel",
                foreground=self.theme["accent"],
            ).pack(anchor="w", pady=(2, 0))

            if entry["details"]:
                ttk.Label(
                    details_frame, text=entry["details"], style="TLabel", wraplength=450
                ).pack(anchor="w", pady=(5, 0))

        # Update the canvas scroll region
        history_list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Add close button at the bottom
        button_frame = ttk.Frame(history_window, style="TFrame")
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Button(
            button_frame,
            text=self._("Close"),
            style="iOS.TButton",
            command=history_window.destroy,
        ).pack(side=tk.RIGHT)
