"""
controllers/race_controller.py - Controller for race management
"""

import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RaceController:
    """
    Controller for race management.
    Handles actions related to updating race results and managing driver substitutions.
    """
    
    def __init__(self, view, data_manager):
        """
        Initialize the race controller.
        
        Args:
            view: The race view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Connect view events to controller methods
        self.connect_view_events()
        
        # Load data
        self.load_data()
    
    def connect_view_events(self):
        """Connect view event handlers to controller methods"""
        self.view.on_update_race = self.update_race_results
        self.view.on_add_substitution = self.add_substitution
        self.view.on_refresh_races = self.load_data
        self.view.on_manual_point_entry = self.show_manual_point_entry
        
        # Connect team and driver selection events for substitution
        if hasattr(self.view, 'sub_team_var'):
            self.view.sub_team_var.trace_add("write", self.update_team_logo)
        if hasattr(self.view, 'sub_original_var'):
            self.view.sub_original_var.trace_add("write", self.update_original_driver)
        if hasattr(self.view, 'sub_substitute_var'):
            self.view.sub_substitute_var.trace_add("write", self.update_substitute_driver)
    
    def load_data(self):
        """Load data from the data manager and update the view"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Update race dropdown options
        races = data['races']
        race_display = [f"{row['RaceID']} - {row['Name']}" for _, row in races.iterrows()]
        self.view.set_race_options(race_display)
        
        # Update team dropdown options
        teams = data['teams']
        team_display = [f"{row['TeamID']} - {row['Name']}" for _, row in teams.iterrows()]
        self.view.set_team_options(team_display)
        
        # Update driver dropdown options
        drivers = data['drivers']
        driver_display = [f"{row['Name']} ({row['DriverID']}) - {row['Credits']} credits" 
                         for _, row in drivers.sort_values(by='Name').iterrows()]
        self.view.set_driver_options(driver_display)
        
        # Update race calendar
        self.update_race_calendar()
        
        # Update substitution list
        self.update_substitutions()
    
    def update_race_calendar(self):
        """Update the race calendar in the view"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Process race data for display
        races = data['races'].sort_values(by='Date')
        race_data = []
        
        for _, race in races.iterrows():
            race_data.append((
                race['RaceID'],
                race['Name'],
                race['Date'].strftime('%Y-%m-%d'),
                race['Status']
            ))
        
        # Update the view
        self.view.update_race_calendar(race_data)
    
    def update_substitutions(self):
        """Update the list of substitutions in the view"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Process substitution data for display
        substitutions = data['driver_assignments']
        drivers = data['drivers']
        teams = data['teams']
        
        sub_data = []
        
        for _, sub in substitutions.iterrows():
            # Get names for display
            original_driver = drivers[drivers['DriverID'] == sub['SubstitutedForDriverID']]
            substitute_driver = drivers[drivers['DriverID'] == sub['DriverID']]
            team = teams[teams['TeamID'] == sub['TeamID']]
            
            original_name = original_driver['Name'].iloc[0] if not original_driver.empty else sub['SubstitutedForDriverID']
            substitute_name = substitute_driver['Name'].iloc[0] if not substitute_driver.empty else sub['DriverID']
            team_name = team['Name'].iloc[0] if not team.empty else sub['TeamID']
            
            sub_data.append((
                sub['RaceID'],
                f"{original_name} ({sub['SubstitutedForDriverID']})",
                f"{substitute_name} ({sub['DriverID']})",
                team_name
            ))
        
        # Update the view
        self.view.update_substitution_list(sub_data)
    
    def update_race_results(self):
        """Update results for a specific race"""
        # Get selected race
        race_selection = self.view.get_selected_race()
        if not race_selection:
            messagebox.showerror("Error", "Please select a race")
            return
        
        # Extract race ID
        race_id = race_selection.split('-')[0].strip()
        
        # Confirm action
        response = messagebox.askyesno(
            "Confirm Update", 
            f"This will scrape race results for {race_id} and update player points.\nContinue?"
        )
        if not response:
            return
        
        # Update race results
        try:
            # Show progress
            self.view.set_status(f"Scraping results for race {race_id}...")
            
            # Fetch race results - this could use our scraper
            from utils.scraper import scrape_race_results
            results = scrape_race_results(race_id)
            
            if not results:
                messagebox.showerror("Error", f"Failed to retrieve results for race {race_id}")
                self.view.set_status("Failed to retrieve race results")
                return
            
            # Save results
            if not self.data_manager.save_race_results(race_id, results):
                messagebox.showerror("Error", "Failed to save race results")
                self.view.set_status("Failed to save race results")
                return
            
            # Calculate player points
            if not self.data_manager.calculate_player_points_for_race(race_id):
                messagebox.showerror("Error", "Failed to calculate player points")
                self.view.set_status("Failed to calculate player points")
                return
            
            # Update race calendar
            self.update_race_calendar()
            
            messagebox.showinfo("Success", f"Race results for {race_id} updated successfully!")
            self.view.set_status(f"Race results for {race_id} updated successfully")
        except Exception as e:
            logger.exception("Error updating race results")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.view.set_status("Error updating race results")
    
    def add_substitution(self):
        """Add a driver substitution"""
        # Get form data
        race_id, team_id, original_id, substitute_id = self.view.get_substitution_data()
        
        # Validate inputs
        if not race_id or not team_id or not original_id or not substitute_id:
            messagebox.showerror("Error", "All fields are required")
            return
        
        # Record substitution
        if not self.data_manager.record_driver_substitution(race_id, substitute_id, team_id, original_id):
            messagebox.showerror("Error", "Failed to record substitution")
            self.view.set_status("Failed to record substitution")
            return
        
        # Recalculate points if race is completed
        data = self.data_manager.load_data()
        if race_id in data['races'][data['races']['Status'] == 'Completed']['RaceID'].values:
            if not self.data_manager.calculate_player_points_for_race(race_id):
                messagebox.showwarning("Warning", "Failed to recalculate player points")
        
        # Update substitution list
        self.update_substitutions()
        
        # Clear form
        self.view.clear_substitution_form()
        
        messagebox.showinfo("Success", 
                           f"Substitution recorded: {substitute_id} replacing {original_id} at {team_id} for race {race_id}")
        self.view.set_status(f"Added substitution: {substitute_id} replacing {original_id} at {team_id} for race {race_id}")
    
    def show_manual_point_entry(self):
        """Show dialog for manual point entry"""
        # Get selected race
        race_selection = self.view.get_selected_race()
        if not race_selection:
            messagebox.showerror("Error", "Please select a race")
            return
        
        # Extract race ID
        race_id = race_selection.split('-')[0].strip()
        
        # Create dialog
        dialog = tk.Toplevel(self.view.frame)
        dialog.title(f"Manual Point Entry for {race_id}")
        dialog.geometry("500x600")
        dialog.transient(self.view.frame)
        dialog.grab_set()
        
        # Load data
        data = self.data_manager.load_data()
        drivers = data['drivers']
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create entry fields for each driver
        point_vars = {}
        
        tk.Label(scrollable_frame, text="Driver").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Points").grid(row=0, column=1, padx=5, pady=5)
        
        for i, (_, driver) in enumerate(drivers.iterrows(), 1):
            tk.Label(scrollable_frame, text=f"{driver['Name']} ({driver['DriverID']})").grid(
                row=i, column=0, padx=5, pady=2, sticky=tk.W)
            
            point_var = tk.StringVar(value="0.0")
            point_vars[driver['DriverID']] = point_var
            
            tk.Entry(scrollable_frame, textvariable=point_var, width=10).grid(
                row=i, column=1, padx=5, pady=2)
        
        def save_points():
            try:
                # Create dataframe for race results
                results_data = []
                
                for driver_id, point_var in point_vars.items():
                    try:
                        points = float(point_var.get())
                        results_data.append({
                            'RaceID': race_id,
                            'DriverID': driver_id,
                            'Points': points
                        })
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid point value for {driver_id}")
                        return
                
                # Save results
                if not self.data_manager.save_race_results(race_id, results_data):
                    messagebox.showerror("Error", "Failed to save race results")
                    return
                
                # Calculate player points
                if not self.data_manager.calculate_player_points_for_race(race_id):
                    messagebox.showerror("Error", "Failed to calculate player points")
                    return
                
                # Update race calendar
                self.update_race_calendar()
                
                messagebox.showinfo("Success", f"Race results for {race_id} saved successfully!")
                dialog.destroy()
                
                self.view.set_status(f"Manually entered points for race {race_id}")
            except Exception as e:
                logger.exception("Error saving points")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Save Points", command=save_points).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_team_logo(self, *args):
        """Update the team logo image"""
        if hasattr(self.view, 'update_team_logo_image'):
            team = self.view.sub_team_var.get()
            if not team:
                return
            
            # Extract team ID
            team_id = team.split('-')[0].strip()
            
            # Get team logo image (placeholder for now)
            from PIL import Image, ImageTk
            placeholder = Image.new('RGB', (50, 50), color=(200, 200, 200))
            team_logo = ImageTk.PhotoImage(placeholder)
            
            self.view.update_team_logo_image(team_logo)
    
    def update_original_driver(self, *args):
        """Update the original driver image"""
        if hasattr(self.view, 'update_original_driver_image'):
            driver = self.view.sub_original_var.get()
            if not driver:
                return
            
            # Extract driver ID
            driver_id = driver.split('(')[1].split(')')[0]
            
            # Get driver image (placeholder for now)
            from PIL import Image, ImageTk
            placeholder = Image.new('RGB', (60, 60), color=(200, 200, 200))
            driver_image = ImageTk.PhotoImage(placeholder)
            
            self.view.update_original_driver_image(driver_image)
    
    def update_substitute_driver(self, *args):
        """Update the substitute driver image"""
        if hasattr(self.view, 'update_substitute_driver_image'):
            driver = self.view.sub_substitute_var.get()
            if not driver:
                return
            
            # Extract driver ID
            driver_id = driver.split('(')[1].split(')')[0]
            
            # Get driver image (placeholder for now)
            from PIL import Image, ImageTk
            placeholder = Image.new('RGB', (60, 60), color=(200, 200, 200))
            driver_image = ImageTk.PhotoImage(placeholder)
            
            self.view.update_substitute_driver_image(driver_image)