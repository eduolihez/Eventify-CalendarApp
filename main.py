import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar, DateEntry
import json
import os
from datetime import datetime

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Calendar")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Set theme colors
        self.colors = {
            "bg": "#f5f5f5",
            "accent": "#3a7ebf",
            "text": "#333333",
            "light_text": "#666666",
            "button": "#4a90e2",
            "button_hover": "#3a7ebf",
            "event_bg": "#e6f2ff",
            "event_border": "#4a90e2"
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Calendar.TFrame', background=self.colors["bg"])
        self.style.configure('TButton', 
                            background=self.colors["button"], 
                            foreground='white', 
                            font=('Arial', 10, 'bold'),
                            padding=5)
        self.style.map('TButton', 
                      background=[('active', self.colors["button_hover"])])
        
        self.root.configure(bg=self.colors["bg"])
        
        # Initialize events storage
        self.events_file = "calendar_events.json"
        self.events = self.load_events()
        
        # Create the main layout
        self.create_widgets()
        
        # Update event markers on calendar
        self.update_calendar_markers()
        
    def load_events(self):
        """Load events from JSON file"""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r') as file:
                    return json.load(file)
            except:
                return {}
        return {}
    
    def save_events(self):
        """Save events to JSON file"""
        with open(self.events_file, 'w') as file:
            json.dump(self.events, file, indent=4)
        
    def create_widgets(self):
        """Create all widgets for the application"""
        # Main frame
        main_frame = ttk.Frame(self.root, style='Calendar.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for calendar
        left_panel = ttk.Frame(main_frame, style='Calendar.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calendar widget
        cal_frame = ttk.Frame(left_panel, style='Calendar.TFrame')
        cal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calendar header
        cal_header = ttk.Frame(cal_frame, style='Calendar.TFrame')
        cal_header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(cal_header, text="Calendar", 
                 font=('Arial', 16, 'bold'), 
                 background=self.colors["bg"],
                 foreground=self.colors["text"]).pack(side=tk.LEFT)
        
        self.month_year_label = ttk.Label(cal_header, 
                                         font=('Arial', 12),
                                         background=self.colors["bg"],
                                         foreground=self.colors["light_text"])
        self.month_year_label.pack(side=tk.RIGHT)
        
        # Calendar
        self.cal = Calendar(cal_frame, 
                           selectmode='day',
                           firstweekday='sunday',
                           showweeknumbers=False,
                           background=self.colors["bg"],
                           foreground=self.colors["text"],
                           bordercolor=self.colors["bg"],
                           headersbackground=self.colors["accent"],
                           headersforeground='white',
                           selectbackground=self.colors["accent"],
                           normalbackground='white',
                           weekendbackground='white',
                           othermonthbackground='#f0f0f0',
                           othermonthwebackground='#f0f0f0',
                           font=('Arial', 10),
                           cursor="hand1")
        self.cal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update month_year_label when date changes
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        self.update_month_year_label()
        
        # Right panel for day view and event details
        right_panel = ttk.Frame(main_frame, style='Calendar.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Day view section
        day_view_frame = ttk.Frame(right_panel, style='Calendar.TFrame')
        day_view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.day_header = ttk.Label(day_view_frame, 
                                   text="Day View", 
                                   font=('Arial', 16, 'bold'),
                                   background=self.colors["bg"],
                                   foreground=self.colors["text"])
        self.day_header.pack(fill=tk.X, padx=5, pady=5)
        
        # Events list
        events_frame = ttk.Frame(day_view_frame, style='Calendar.TFrame')
        events_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for events list
        scrollbar = ttk.Scrollbar(events_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.events_list = tk.Listbox(events_frame, 
                                     height=10, 
                                     font=('Arial', 10),
                                     bg='white',
                                     fg=self.colors["text"],
                                     selectbackground=self.colors["accent"],
                                     selectforeground='white',
                                     yscrollcommand=scrollbar.set)
        self.events_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.events_list.yview)
        
        # Bind double click on event list to edit
        self.events_list.bind('<Double-1>', self.edit_selected_event)
        
        # Buttons for event management
        button_frame = ttk.Frame(right_panel, style='Calendar.TFrame')
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        add_btn = ttk.Button(button_frame, text="Add Event", command=self.add_event)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(button_frame, text="Edit Event", command=self.edit_event)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="Delete Event", command=self.delete_event)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Event form section (initially hidden)
        self.event_form_frame = ttk.Frame(right_panel, style='Calendar.TFrame')
        
        # Form fields
        form_fields = ttk.Frame(self.event_form_frame, style='Calendar.TFrame')
        form_fields.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title field
        ttk.Label(form_fields, text="Event Title:", 
                 background=self.colors["bg"],
                 foreground=self.colors["text"]).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(form_fields, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Date field with DateEntry widget
        ttk.Label(form_fields, text="Date:", 
                 background=self.colors["bg"],
                 foreground=self.colors["text"]).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        date_frame = ttk.Frame(form_fields, style='Calendar.TFrame')
        date_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.date_picker = DateEntry(date_frame, 
                                    width=12, 
                                    background=self.colors["accent"],
                                    foreground='white',
                                    borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
        self.date_picker.pack(side=tk.LEFT)
        
        # Time field with dropdown
        ttk.Label(form_fields, text="Time:", 
                 background=self.colors["bg"],
                 foreground=self.colors["text"]).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.time_var = tk.StringVar()
        
        # Create time options in 30-minute increments
        time_options = []
        for hour in range(24):
            time_options.append(f"{hour:02d}:00")
            time_options.append(f"{hour:02d}:30")
        
        time_dropdown = ttk.Combobox(form_fields, 
                                    textvariable=self.time_var, 
                                    values=time_options,
                                    width=10,
                                    state="readonly")
        time_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Description field
        ttk.Label(form_fields, text="Description:", 
                 background=self.colors["bg"],
                 foreground=self.colors["text"]).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_text = tk.Text(form_fields, height=5, width=30)
        self.desc_text.grid(row=3, column=1, padx=5, pady=5)
        
        # Form buttons
        form_buttons = ttk.Frame(self.event_form_frame, style='Calendar.TFrame')
        form_buttons.pack(fill=tk.X, padx=5, pady=10)
        
        self.save_btn = ttk.Button(form_buttons, text="Save Event", command=self.save_event)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(form_buttons, text="Cancel", command=self.cancel_form)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize with current date selected
        self.on_date_select(None)
    
    def update_month_year_label(self):
        """Update the month and year label based on current calendar view"""
        date = self.cal.get_displayed_month()
        month_name = datetime(2000, date[0], 1).strftime('%B')
        self.month_year_label.config(text=f"{month_name} {date[1]}")
    
    def on_date_select(self, event):
        """Handle date selection on calendar"""
        selected_date = self.cal.get_date()
        date_obj = datetime.strptime(selected_date, '%m/%d/%y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        self.current_date = formatted_date
        self.day_header.config(text=f"Events for {date_obj.strftime('%B %d, %Y')}")
        
        # Update the events list
        self.update_events_list()
    
    def update_events_list(self):
        """Update the events list for the selected date"""
        self.events_list.delete(0, tk.END)
        
        if self.current_date in self.events:
            # Sort events by time
            day_events = sorted(self.events[self.current_date], 
                               key=lambda x: x['time'] if 'time' in x else '00:00')
            
            for event in day_events:
                time_str = event.get('time', '')
                title = event.get('title', 'Untitled Event')
                if time_str:
                    self.events_list.insert(tk.END, f"{time_str} - {title}")
                else:
                    self.events_list.insert(tk.END, title)
    
    def update_calendar_markers(self):
        """Mark dates that have events"""
        # Clear all marks first
        for date in self.events:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%m/%d/%y')
                self.cal.calevent_remove(formatted_date)
            except:
                continue
        
        # Add new marks
        for date in self.events:
            if self.events[date]:  # If there are events on this date
                try:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%m/%d/%y')
                    self.cal.calevent_create(date=formatted_date, text="Event", tags=["event"])
                except:
                    continue
        
        # Configure tag
        self.cal.tag_config("event", background=self.colors["event_bg"], foreground=self.colors["text"])
    
    def add_event(self):
        """Open form to add a new event"""
        # Clear form fields
        self.title_var.set("")
        
        # Set date picker to current selected date
        current_date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')
        self.date_picker.set_date(current_date_obj)
        
        # Clear time and description
        self.time_var.set("")
        self.desc_text.delete(1.0, tk.END)
        
        # Hide events list and show form
        self.events_list.pack_forget()
        self.event_form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set form mode
        self.form_mode = "add"
        self.selected_event_index = None
    
    def edit_event(self):
        """Edit the selected event"""
        if not self.events_list.curselection():
            messagebox.showinfo("Info", "Please select an event to edit")
            return
        
        self.edit_selected_event(None)
    
    def edit_selected_event(self, event):
        """Handle editing of the selected event"""
        if not self.events_list.curselection():
            return
        
        index = self.events_list.curselection()[0]
        
        if self.current_date in self.events and index < len(self.events[self.current_date]):
            selected_event = self.events[self.current_date][index]
            
            # Fill form with event data
            self.title_var.set(selected_event.get('title', ''))
            
            # Set date picker to event date
            event_date_obj = datetime.strptime(self.current_date, '%Y-%m-%d')
            self.date_picker.set_date(event_date_obj)
            
            # Set time dropdown
            self.time_var.set(selected_event.get('time', ''))
            
            # Set description
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(tk.END, selected_event.get('description', ''))
            
            # Hide events list and show form
            self.events_list.pack_forget()
            self.event_form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Set form mode
            self.form_mode = "edit"
            self.selected_event_index = index
    
    def delete_event(self):
        """Delete the selected event"""
        if not self.events_list.curselection():
            messagebox.showinfo("Info", "Please select an event to delete")
            return
        
        index = self.events_list.curselection()[0]
        
        if self.current_date in self.events and index < len(self.events[self.current_date]):
            confirm = messagebox.askyesno("Confirm Delete", 
                                         "Are you sure you want to delete this event?")
            if confirm:
                # Remove the event
                self.events[self.current_date].pop(index)
                
                # If no more events on this date, remove the date
                if not self.events[self.current_date]:
                    del self.events[self.current_date]
                
                # Save events and update display
                self.save_events()
                self.update_events_list()
                self.update_calendar_markers()
    
    def save_event(self):
        """Save the event data from the form"""
        # Get data from form
        title = self.title_var.get().strip()
        
        # Get date from DateEntry widget
        date_obj = self.date_picker.get_date()
        date = date_obj.strftime('%Y-%m-%d')
        
        # Get time from dropdown
        time = self.time_var.get().strip()
        
        # Get description
        description = self.desc_text.get(1.0, tk.END).strip()
        
        # Validate data
        if not title:
            messagebox.showwarning("Warning", "Please enter an event title")
            return
        
        # Create event object
        event = {
            'title': title,
            'time': time,
            'description': description
        }
        
        # Add or update the event
        if date not in self.events:
            self.events[date] = []
        
        if self.form_mode == "edit" and self.selected_event_index is not None:
            # Update existing event
            if date == self.current_date:
                self.events[date][self.selected_event_index] = event
            else:
                # Event date was changed, remove from current date and add to new date
                self.events[self.current_date].pop(self.selected_event_index)
                if not self.events[self.current_date]:
                    del self.events[self.current_date]
                self.events[date].append(event)
        else:
            # Add new event
            self.events[date].append(event)
        
        # Save events and update display
        self.save_events()
        
        # If the event date is the current displayed date, update the list
        if date == self.current_date:
            self.update_events_list()
        else:
            # If date changed, select the new date in the calendar
            try:
                # Format for calendar widget
                cal_date = date_obj.strftime('%m/%d/%y')
                self.cal.selection_set(cal_date)
                self.on_date_select(None)
            except:
                pass
        
        # Update calendar markers for all dates
        self.update_calendar_markers()
        
        # Close the form
        self.cancel_form()
    
    def cancel_form(self):
        """Cancel the event form and return to events list"""
        self.event_form_frame.pack_forget()
        self.events_list.pack(fill=tk.BOTH, expand=True)

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
    print("Calendar application closed")