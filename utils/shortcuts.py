import tkinter as tk

class ShortcutManager:
    """Manages keyboard shortcuts for the application"""
    
    def __init__(self, app):
        """Initialize the shortcut manager"""
        self.app = app
        self.root = app.root
        
        # Register standard shortcuts
        self.register_shortcuts()
    
    def register_shortcuts(self):
        """Register all keyboard shortcuts"""
        # File menu shortcuts
        self.root.bind("<Control-n>", lambda e: self.app.create_event())
        self.root.bind("<Control-o>", lambda e: self.app.import_events())
        self.root.bind("<Control-s>", lambda e: self.app.export_events())
        
        # Edit menu shortcuts
        self.root.bind("<Control-f>", lambda e: self.app.search_events())
        
        # View menu shortcuts
        self.root.bind("<Control-t>", lambda e: self.app.go_to_today())
        
        # Navigation shortcuts
        self.root.bind("<Left>", lambda e: self.app.previous_period())
        self.root.bind("<Right>", lambda e: self.app.next_period())
        
        # Tab navigation
        self.root.bind("<Control-Tab>", lambda e: self.next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self.previous_tab())
    
    def next_tab(self):
        """Switch to the next tab"""
        current = self.app.notebook.index("current")
        if current < self.app.notebook.index("end") - 1:
            self.app.notebook.select(current + 1)
        else:
            self.app.notebook.select(0)
    
    def previous_tab(self):
        """Switch to the previous tab"""
        current = self.app.notebook.index("current")
        if current > 0:
            self.app.notebook.select(current - 1)
        else:
            self.app.notebook.select(self.app.notebook.index("end") - 1)