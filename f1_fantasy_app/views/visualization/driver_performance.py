"""
views/visualization/driver_performance.py - Driver performance visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np

class DriverPerformanceVisualization(BaseVisualization):
    """Driver performance visualization showing driver performance across races"""
    
    def __init__(self, parent, controller):
        """
        Initialize the driver performance visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        driver_frame = ttk.Frame(self.controls_frame)
        driver_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(driver_frame, text="Select Drivers:").pack(side=tk.TOP, padx=5, pady=5)
        
        # Create multi-select listbox with scrollbar
        select_frame = ttk.Frame(driver_frame)
        select_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(select_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.driver_listbox = tk.Listbox(select_frame, selectmode=tk.MULTIPLE, 
                                        height=4, width=30, yscrollcommand=scrollbar.set)
        self.driver_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.driver_listbox.yview)
        
        # Add update button
        ttk.Button(self.controls_frame, text="Update Chart", 
                  command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Driver Performance"
    
    def set_driver_options(self, driver_options):
        """Set the options for the driver listbox
        
        Args:
            driver_options (list): List of driver option strings
        """
        # Clear existing options
        self.driver_listbox.delete(0, tk.END)
        
        # Add new options
        for option in driver_options:
            self.driver_listbox.insert(tk.END, option)
    
    def get_selected_drivers(self):
        """Get the selected drivers from the listbox
        
        Returns:
            list: List of selected driver IDs
        """
        selections = self.driver_listbox.curselection()
        if not selections:
            return []
        
        selected_items = [self.driver_listbox.get(i) for i in selections]
        selected_ids = [item.split('(')[1].split(')')[0] for item in selected_items]
        
        return selected_ids
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Dictionary containing:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - driver_data (list): List of dictionaries with driver data:
                    - driver_id (str): Driver ID
                    - driver_name (str): Driver name
                    - race_points (list): List of points for each race
                    - avg_points (float): Average points per race
        """
        if not data or not data.get('driver_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        completed_races = data.get('completed_races', [])
        race_dates = data.get('race_dates', {})
        driver_data = data.get('driver_data', [])
        
        # Clear previous plot
        self.ax.clear()
        
        # Plot points for each selected driver
        for driver in driver_data:
            driver_id = driver['driver_id']
            driver_name = driver['driver_name']
            race_points = driver['race_points']
            
            self.ax.plot(completed_races, race_points, marker='o', linewidth=2, 
                       label=f"{driver_name} ({driver_id})")
        
        # Formatting
        self.ax.set_title('Driver Performance Across Races', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Race', fontsize=12)
        self.ax.set_ylabel('Points', fontsize=12)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper left', fontsize=10)
        
        # Add race annotations
        for i, race_id in enumerate(completed_races):
            if i % 2 == 0:  # Annotate every other race to avoid clutter
                self.ax.annotate(f"{race_id}\n{race_dates.get(race_id, '')}", 
                               xy=(race_id, 0), 
                               xytext=(0, -25),
                               textcoords='offset points',
                               ha='center', fontsize=8)
        
        # Add average line for each driver
        for driver in driver_data:
            driver_name = driver['driver_name']
            avg_points = driver['avg_points']
            
            self.ax.axhline(y=avg_points, color='gray', linestyle='--', alpha=0.5)
            self.ax.annotate(f"Avg: {avg_points:.1f}", 
                           xy=(completed_races[-1], avg_points),
                           xytext=(5, 0),
                           textcoords="offset points",
                           fontsize=8, color='gray')
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            selected_drivers = self.get_selected_drivers()
            if not selected_drivers:
                self.show_placeholder("Please select at least one driver")
                return
            
            self.controller.update_visualization(selected_drivers)