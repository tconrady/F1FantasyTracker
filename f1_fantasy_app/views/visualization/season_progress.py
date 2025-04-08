"""
views/visualization/season_progress.py - Season progress visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np

class SeasonProgressVisualization(BaseVisualization):
    """Season progress visualization showing cumulative points over races"""
    
    def __init__(self, parent, controller):
        """
        Initialize the season progress visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        ttk.Button(self.controls_frame, text="Update Visualization", 
                   command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
        
    def get_title(self):
        """Get the title for this visualization"""
        return "Season Progress"
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Dictionary containing:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - player_data (list): List of dictionaries with player data:
                    - player_id (str): Player ID
                    - player_name (str): Player name
                    - cumulative_points (list): List of cumulative points for each race
        """
        if not data or not data.get('player_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        completed_races = data.get('completed_races', [])
        race_dates = data.get('race_dates', {})
        player_data = data.get('player_data', [])
        
        # Clear previous plot
        self.ax.clear()
        
        # Plot cumulative points for each player
        for player in player_data:
            player_name = player['player_name']
            cumulative_points = player['cumulative_points']
            
            self.ax.plot(completed_races, cumulative_points, marker='o', linewidth=2, label=player_name)
        
        # Formatting
        self.ax.set_title('Cumulative F1 Fantasy Points by Player', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Race', fontsize=12)
        self.ax.set_ylabel('Cumulative Points', fontsize=12)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper left', fontsize=10)
        
        # Add race annotations
        for i, race_id in enumerate(completed_races):
            if i % 2 == 0:  # Annotate every other race to avoid clutter
                race_date = race_dates.get(race_id, "")
                self.ax.annotate(f"{race_id}\n{race_date}", 
                               xy=(race_id, 0), 
                               xytext=(0, -25),
                               textcoords='offset points',
                               ha='center', fontsize=8)
        
        # Add point markers with exact values
        for player in player_data:
            player_name = player['player_name']
            cumulative_points = player['cumulative_points']
            
            # Get the line data from the plot
            for line in self.ax.get_lines():
                if line.get_label() == player_name:
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    
                    # Only annotate the final point
                    i = len(x_data) - 1
                    self.ax.annotate(f"{y_data[i]:.1f}", 
                                   xy=(x_data[i], y_data[i]),
                                   xytext=(5, 0),
                                   textcoords='offset points',
                                   fontsize=9, fontweight='bold')
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            self.controller.update_visualization()