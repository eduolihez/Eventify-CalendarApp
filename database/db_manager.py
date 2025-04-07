import sqlite3
import os
from datetime import datetime, timedelta

class DatabaseManager:
    """Manages all database operations for the calendar application"""
    
    def __init__(self, db_path="calendar.db"):
        """Initialize the database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
    
    def setup_database(self):
        """Create the necessary tables if they don't exist"""
        # Events table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            location TEXT,
            priority TEXT DEFAULT 'medium',
            color TEXT,
            is_recurring INTEGER DEFAULT 0,
            recurrence_type TEXT,
            recurrence_end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Event history table for tracking changes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
        ''')
        
        # Settings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        )
        ''')
        
        # Insert default settings if they don't exist
        default_settings = [
            ('theme', 'light'),
            ('language', 'en'),
            ('notification_time', '15'),  # minutes before event
        ]
        
        for key, value in default_settings:
            self.cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
        
        self.conn.commit()
    
    def add_event(self, event_data):
        """Add a new event to the database"""
        query = '''
        INSERT INTO events (
            title, description, start_time, end_time, location, 
            priority, color, is_recurring, recurrence_type, recurrence_end_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.cursor.execute(query, (
            event_data['title'],
            event_data.get('description', ''),
            event_data['start_time'],
            event_data['end_time'],
            event_data.get('location', ''),
            event_data.get('priority', 'medium'),
            event_data.get('color', '#3498db'),
            1 if event_data.get('is_recurring', False) else 0,
            event_data.get('recurrence_type', None),
            event_data.get('recurrence_end_date', None)
        ))
        
        event_id = self.cursor.lastrowid
        
        # Log the event creation in history
        self.log_event_history(event_id, 'create', 'Event created')
        
        self.conn.commit()
        return event_id
    
    def update_event(self, event_id, event_data):
        """Update an existing event"""
        query = '''
        UPDATE events SET
            title = ?,
            description = ?,
            start_time = ?,
            end_time = ?,
            location = ?,
            priority = ?,
            color = ?,
            is_recurring = ?,
            recurrence_type = ?,
            recurrence_end_date = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        '''
        
        self.cursor.execute(query, (
            event_data['title'],
            event_data.get('description', ''),
            event_data['start_time'],
            event_data['end_time'],
            event_data.get('location', ''),
            event_data.get('priority', 'medium'),
            event_data.get('color', '#3498db'),
            1 if event_data.get('is_recurring', False) else 0,
            event_data.get('recurrence_type', None),
            event_data.get('recurrence_end_date', None),
            event_id
        ))
        
        # Log the event update in history
        self.log_event_history(event_id, 'update', 'Event updated')
        
        self.conn.commit()
        return True
    
    def delete_event(self, event_id):
        """Delete an event from the database"""
        self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        
        # Log the event deletion in history
        self.log_event_history(event_id, 'delete', 'Event deleted')
        
        self.conn.commit()
        return True
    
    def get_event(self, event_id):
        """Get a single event by ID"""
        self.cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        return dict(self.cursor.fetchone())
    
    def get_events_by_date_range(self, start_date, end_date):
        """Get all events within a date range"""
        query = """
        SELECT * FROM events 
        WHERE (start_time BETWEEN ? AND ?) 
           OR (end_time BETWEEN ? AND ?)
           OR (start_time <= ? AND end_time >= ?)
        ORDER BY start_time
        """
        
        self.cursor.execute(query, (
            start_date, end_date,
            start_date, end_date,
            start_date, end_date
        ))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_events(self, search_term, start_date=None, end_date=None):
        """Search events by title, description, or location"""
        search_term = f"%{search_term}%"
        
        if start_date and end_date:
            query = """
            SELECT * FROM events 
            WHERE (title LIKE ? OR description LIKE ? OR location LIKE ?)
            AND ((start_time BETWEEN ? AND ?) 
               OR (end_time BETWEEN ? AND ?)
               OR (start_time <= ? AND end_time >= ?))
            ORDER BY start_time
            """
            
            self.cursor.execute(query, (
                search_term, search_term, search_term,
                start_date, end_date,
                start_date, end_date,
                start_date, end_date
            ))
        else:
            query = """
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
            ORDER BY start_time
            """
            
            self.cursor.execute(query, (search_term, search_term, search_term))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_upcoming_events(self, minutes=15):
        """Get events that will start in the next X minutes"""
        now = datetime.now()
        notification_time = now + timedelta(minutes=minutes)
        
        query = """
        SELECT * FROM events 
        WHERE start_time BETWEEN ? AND ?
        ORDER BY start_time
        """
        
        self.cursor.execute(query, (now.strftime('%Y-%m-%d %H:%M:%S'), 
                                   notification_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def log_event_history(self, event_id, action, details):
        """Log an event history entry"""
        query = """
        INSERT INTO event_history (event_id, action, details)
        VALUES (?, ?, ?)
        """
        
        self.cursor.execute(query, (event_id, action, details))
        self.conn.commit()
    
    def get_event_history(self, event_id):
        """Get the history for a specific event"""
        query = """
        SELECT * FROM event_history
        WHERE event_id = ?
        ORDER BY timestamp DESC
        """
        
        self.cursor.execute(query, (event_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_setting(self, key):
        """Get a setting value by key"""
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None
    
    def update_setting(self, key, value):
        """Update a setting value"""
        self.cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()