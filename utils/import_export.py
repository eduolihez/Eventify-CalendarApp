import csv
import os
from datetime import datetime, timedelta
import re

# Try to import icalendar for .ics support
try:
    import icalendar
    from icalendar import Calendar, Event
    ICAL_AVAILABLE = True
except ImportError:
    ICAL_AVAILABLE = False

class ImportExportManager:
    """Manages importing and exporting events"""
    
    def __init__(self, db_manager):
        """Initialize the import/export manager"""
        self.db_manager = db_manager
    
    def import_events(self, file_path):
        """Import events from a file"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.ics' and ICAL_AVAILABLE:
            return self.import_from_ical(file_path)
        elif file_ext == '.csv':
            return self.import_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def import_from_ical(self, file_path):
        """Import events from an iCalendar file"""
        if not ICAL_AVAILABLE:
            raise ImportError("icalendar package is not installed. Please install it with 'pip install icalendar'")
        
        with open(file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        count = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                # Extract event data
                summary = str(component.get('summary', 'Imported Event'))
                description = str(component.get('description', ''))
                location = str(component.get('location', ''))
                
                # Get start and end times
                start = component.get('dtstart').dt
                end = component.get('dtend').dt if component.get('dtend') else (start + timedelta(hours=1))
                
                # Convert to datetime if it's a date
                if not isinstance(start, datetime):
                    start = datetime.combine(start, datetime.min.time())
                if not isinstance(end, datetime):
                    end = datetime.combine(end, datetime.min.time())
                
                # Check for recurring events
                rrule = component.get('rrule')
                is_recurring = bool(rrule)
                recurrence_type = None
                recurrence_end_date = None
                
                if is_recurring:
                    # Extract recurrence information
                    freq = rrule.get('FREQ', ['DAILY'])[0]
                    if freq == 'DAILY':
                        recurrence_type = 'daily'
                    elif freq == 'WEEKLY':
                        recurrence_type = 'weekly'
                    elif freq == 'MONTHLY':
                        recurrence_type = 'monthly'
                    elif freq == 'YEARLY':
                        recurrence_type = 'yearly'
                    
                    # Get end date if available
                    until = rrule.get('UNTIL')
                    if until and until[0]:
                        recurrence_end_date = until[0].strftime("%Y-%m-%d %H:%M:%S")
                
                # Create event data
                event_data = {
                    "title": summary,
                    "description": description,
                    "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end.strftime("%Y-%m-%d %H:%M:%S"),
                    "location": location,
                    "is_recurring": is_recurring,
                    "recurrence_type": recurrence_type,
                    "recurrence_end_date": recurrence_end_date
                }
                
                # Add to database
                self.db_manager.add_event(event_data)
                count += 1
        
        return count
    
    def import_from_csv(self, file_path):
        """Import events from a CSV file"""
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check required fields
            required_fields = ['title', 'start_time']
            for field in required_fields:
                if field not in reader.fieldnames:
                    raise ValueError(f"CSV file is missing required field: {field}")
            
            count = 0
            for row in reader:
                # Extract event data
                title = row.get('title', '').strip()
                if not title:
                    continue  # Skip events without a title
                
                # Parse start and end times
                try:
                    start_time = self.parse_datetime(row.get('start_time', ''))
                    
                    # If end_time is not provided, default to start_time + 1 hour
                    if 'end_time' in row and row['end_time'].strip():
                        end_time = self.parse_datetime(row['end_time'])
                    else:
                        end_time = start_time + timedelta(hours=1)
                except ValueError as e:
                    # Skip events with invalid dates
                    continue
                
                # Create event data
                event_data = {
                    "title": title,
                    "description": row.get('description', '').strip(),
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "location": row.get('location', '').strip(),
                    "priority": row.get('priority', 'medium').strip().lower(),
                    "color": row.get('color', '#3498db').strip(),
                    "is_recurring": row.get('is_recurring', '').lower() in ('true', 'yes', '1'),
                    "recurrence_type": row.get('recurrence_type', '').strip().lower() or None,
                    "recurrence_end_date": self.parse_datetime(row.get('recurrence_end_date', '')).strftime("%Y-%m-%d %H:%M:%S") if row.get('recurrence_end_date', '').strip() else None
                }
                
                # Add to database
                self.db_manager.add_event(event_data)
                count += 1
            
            return count
    
    def parse_datetime(self, date_string):
        """Parse a datetime string in various formats"""
        if not date_string:
            return datetime.now()
        
        # Try different formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_string, fmt)
                return dt
            except ValueError:
                continue
        
        # If all formats fail, raise an error
        raise ValueError(f"Could not parse date: {date_string}")
    
    def export_to_csv(self, events, file_path):
        """Export events to a CSV file"""
        fieldnames = [
            'title', 'description', 'start_time', 'end_time', 'location',
            'priority', 'color', 'is_recurring', 'recurrence_type', 'recurrence_end_date'
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                # Convert boolean to string
                event_copy = event.copy()
                event_copy['is_recurring'] = 'yes' if event_copy.get('is_recurring') else 'no'
                
                writer.writerow(event_copy)
    
    def export_to_ical(self, events, file_path):
        """Export events to an iCalendar file"""
        if not ICAL_AVAILABLE:
            raise ImportError("icalendar package is not installed. Please install it with 'pip install icalendar'")
        
        cal = Calendar()
        cal.add('prodid', '-//Calendar & Event Manager//EN')
        cal.add('version', '2.0')
        
        for event_data in events:
            event = Event()
            
            # Add basic event properties
            event.add('summary', event_data['title'])
            event.add('description', event_data.get('description', ''))
            event.add('location', event_data.get('location', ''))
            
            # Add start and end times
            start_time = datetime.fromisoformat(event_data['start_time'])
            end_time = datetime.fromisoformat(event_data['end_time'])
            event.add('dtstart', start_time)
            event.add('dtend', end_time)
            
            # Add creation timestamp
            event.add('dtstamp', datetime.now())
            
            # Add a unique identifier
            event.add('uid', f"{event_data['id']}@calendarapp")
            
            # Add recurrence rule if applicable
            if event_data.get('is_recurring'):
                recurrence_type = event_data.get('recurrence_type', 'daily')
                
                # Map recurrence type to iCalendar frequency
                freq_map = {
                    'daily': 'DAILY',
                    'weekly': 'WEEKLY',
                    'monthly': 'MONTHLY',
                    'yearly': 'YEARLY'
                }
                
                freq = freq_map.get(recurrence_type, 'DAILY')
                
                # Create the recurrence rule
                rrule = {'FREQ': [freq]}
                
                # Add end date if available
                if event_data.get('recurrence_end_date'):
                    until = datetime.fromisoformat(event_data['recurrence_end_date'])
                    rrule['UNTIL'] = [until]
                
                event.add('rrule', rrule)
            
            # Add the event to the calendar
            cal.add_component(event)
        
        # Write to file
        with open(file_path, 'wb') as f:
            f.write(cal.to_ical())