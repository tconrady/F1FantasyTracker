"""
views/race_view.py - View for race management
"""

import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView

class RaceView(BaseView):
    """View for race management"""
    
    def __init__(self, parent):
        """
        Initialize the race view.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        
        # Split into left and right frames
        self.left_frame = ttk.Frame(self.frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_frame = ttk.Frame(self.frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set up the left frame (race calendar and update results)
        self.setup_update_race_frame()
        self.setup_race_calendar()
        
        # Set up the right frame (substitutions)
        self.setup_substitution_frame()
        self.setup_substitution_list()
    
    def setup_update_race_frame(self):
        """Set up the update race results frame"""
        update_race_frame = ttk.LabelFrame(self.left_frame, text="Update Race Results")
        update_race_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(update_race_frame, text="Select Race:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.update_race_var = tk.StringVar()
        self.race_selector = ttk.Combobox(update_race_frame, textvariable=self.update_race_var, state="readonly")
        self.race_selector.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(update_race_frame, text="Scrape & Update Results", 
                  command=self.on_update_race).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(update_race_frame, text="Manual Point Entry", 
                  command=self.on_manual_point_entry).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
    
    def setup_race_calendar(self):
        """Set up the race calendar section"""
        calendar_frame = ttk.LabelFrame(self.left_frame, text="2025 Race Calendar")
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for race calendar
        columns = ("RaceID", "Name", "Date", "Status")
        self.race_tree = ttk.Treeview(calendar_frame, columns=columns, show="headings")
        
        # Set column headings
        self.race_tree.heading("RaceID", text="ID")
        self.race_tree.heading("Name", text="Grand Prix")
        self.race_tree.heading("Date", text="Date")
        self.race_tree.heading("Status", text="Status")
        
        # Set column widths
        self.race_tree.column("RaceID", width=50)
        self.race_tree.column("Name", width=200)
        self.race_tree.column("Date", width=100)
        self.race_tree.column("Status", width=100)
        
        # Add a scrollbar
        race_scrollbar = ttk.Scrollbar(calendar_frame, orient=tk.VERTICAL, command=self.race_tree.yview)
        self.race_tree.configure(yscrollcommand=race_scrollbar.set)
        
        self.race_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        race_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_substitution_frame(self):
        """Set up the substitution form frame"""
        sub_frame = ttk.LabelFrame(self.right_frame, text="Add Driver Substitution")
        sub_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(sub_frame, text="Select Race:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sub_race_var = tk.StringVar()
        self.sub_race_dropdown = ttk.Combobox(sub_frame, textvariable=self.sub_race_var, state="readonly")
        self.sub_race_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(sub_frame, text="Team:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sub_team_var = tk.StringVar()
        self.sub_team_dropdown = ttk.Combobox(sub_frame, textvariable=self.sub_team_var, state="readonly")
        self.sub_team_dropdown.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Team logo placeholder
        self.team_logo_label = ttk.Label(sub_frame)
        self.team_logo_label.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(sub_frame, text="Original Driver:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.sub_original_var = tk.StringVar()
        self.sub_original_dropdown = ttk.Combobox(sub_frame, textvariable=self.sub_original_var, state="readonly")
        self.sub_original_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Original driver image placeholder
        self.original_driver_label = ttk.Label(sub_frame)
        self.original_driver_label.grid(row=2, column=2, padx=5, pady=5)
        
        ttk.Label(sub_frame, text="Substitute Driver:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.sub_substitute_var = tk.StringVar()
        self.sub_substitute_dropdown = ttk.Combobox(sub_frame, textvariable=self.sub_substitute_var, state="readonly")
        self.sub_substitute_dropdown.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Substitute driver image placeholder
        self.substitute_driver_label = ttk.Label(sub_frame)
        self.substitute_driver_label.grid(row=3, column=2, padx=5, pady=5)
        
        ttk.Button(sub_frame, text="Add Substitution", 
                  command=self.on_add_substitution).grid(row=4, column=0, columnspan=3, padx=5, pady=10)
    
    def setup_substitution_list(self):
        """Set up the substitution list section"""
        sub_list_frame = ttk.LabelFrame(self.right_frame, text="Current Substitutions")
        sub_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for substitutions
        columns = ("RaceID", "Original", "Substitute", "Team")
        self.sub_tree = ttk.Treeview(sub_list_frame, columns=columns, show="headings")
        
        # Set column headings
        self.sub_tree.heading("RaceID", text="Race")
        self.sub_tree.heading("Original", text="Original Driver")
        self.sub_tree.heading("Substitute", text="Substitute")
        self.sub_tree.heading("Team", text="Team")
        
        # Set column widths
        self.sub_tree.column("RaceID", width=50)
        self.sub_tree.column("Original", width=150)
        self.sub_tree.column("Substitute", width=150)
        self.sub_tree.column("Team", width=100)
        
        # Add a scrollbar
        sub_scrollbar = ttk.Scrollbar(sub_list_frame, orient=tk.VERTICAL, command=self.sub_tree.yview)
        self.sub_tree.configure(yscrollcommand=sub_scrollbar.set)
        
        self.sub_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sub_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button to refresh substitutions
        ttk.Button(self.right_frame, text="Refresh Substitutions", 
                  command=self.on_refresh_substitutions).pack(padx=5, pady=5)
    
    def set_race_options(self, race_options):
        """Set the options for race dropdowns
        
        Args:
            race_options (list): List of race option strings
        """
        self.race_selector['values'] = race_options
        self.sub_race_dropdown['values'] = race_options
    
    def set_team_options(self, team_options):
        """Set the options for team dropdown
        
        Args:
            team_options (list): List of team option strings
        """
        self.sub_team_dropdown['values'] = team_options
    
    def set_driver_options(self, driver_options):
        """Set the options for driver dropdowns
        
        Args:
            driver_options (list): List of driver option strings
        """
        self.sub_original_dropdown['values'] = driver_options
        self.sub_substitute_dropdown['values'] = driver_options
    
    def update_race_calendar(self, race_data):
        """Update the race calendar with new data
        
        Args:
            race_data (list): List of race data tuples (id, name, date, status)
        """
        # Clear existing items
        for item in self.race_tree.get_children():
            self.race_tree.delete(item)
        
        # Add new items
        for race in race_data:
            self.race_tree.insert('', tk.END, values=race)
    
    def update_substitution_list(self, sub_data):
        """Update the substitution list with new data
        
        Args:
            sub_data (list): List of substitution data tuples (race_id, original, substitute, team)
        """
        # Clear existing items
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
        
        # Add new items
        for sub in sub_data:
            self.sub_tree.insert('', tk.END, values=sub)
    
    def get_selected_race(self):
        """Get the selected race from the update race dropdown
        
        Returns:
            str: Selected race or empty string if none selected
        """
        return self.update_race_var.get()
    
    def get_substitution_data(self):
        """Get the data from the substitution form
        
        Returns:
            tuple: (race_id, team_id, original_driver_id, substitute_driver_id)
        """
        race_selection = self.sub_race_var.get()
        team_selection = self.sub_team_var.get()
        original_selection = self.sub_original_var.get()
        substitute_selection = self.sub_substitute_var.get()
        
        # Extract IDs
        race_id = race_selection.split('-')[0].strip() if race_selection else ""
        team_id = team_selection.split('-')[0].strip() if team_selection else ""
        
        original_id = original_selection.split('(')[1].split(')')[0] if '(' in original_selection else ""
        substitute_id = substitute_selection.split('(')[1].split(')')[0] if '(' in substitute_selection else ""
        
        return race_id, team_id, original_id, substitute_id
    
    def clear_substitution_form(self):
        """Clear the substitution form"""
        self.sub_race_var.set("")
        self.sub_team_var.set("")
        self.sub_original_var.set("")
        self.sub_substitute_var.set("")
        self.update_team_logo_image(None)
        self.update_original_driver_image(None)
        self.update_substitute_driver_image(None)
    
    def update_team_logo_image(self, image):
        """Update the team logo image
        
        Args:
            image: PhotoImage object or None
        """
        if image:
            self.team_logo_label.configure(image=image)
            self.team_logo = image  # Keep a reference
        else:
            self.team_logo_label.configure(image='')
    
    def update_original_driver_image(self, image):
        """Update the original driver image
        
        Args:
            image: PhotoImage object or None
        """
        if image:
            self.original_driver_label.configure(image=image)
            self.original_driver_image = image  # Keep a reference
        else:
            self.original_driver_label.configure(image='')
    
    def update_substitute_driver_image(self, image):
        """Update the substitute driver image
        
        Args:
            image: PhotoImage object or None
        """
        if image:
            self.substitute_driver_label.configure(image=image)
            self.substitute_driver_image = image  # Keep a reference
        else:
            self.substitute_driver_label.configure(image='')
    
    def set_status(self, message):
        """Set a status message
        
        Args:
            message (str): Status message
        """
        # This would typically be handled by the main view, but we'll
        # provide a placeholder implementation that could be used by the controller
        pass
    
    # Event handlers - to be overridden by controller
    def on_update_race(self):
        """Handle update race button click"""
        pass
    
    def on_manual_point_entry(self):
        """Handle manual point entry button click"""
        pass
    
    def on_add_substitution(self):
        """Handle add substitution button click"""
        pass
    
    def on_refresh_substitutions(self):
        """Handle refresh substitutions button click"""
        self.on_refresh_races()
    
    def on_refresh_races(self):
        """Handle refresh races button click"""
        pass