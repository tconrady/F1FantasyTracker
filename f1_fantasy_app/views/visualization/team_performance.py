"""
views/visualization/team_performance.py - Team performance visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

class TeamPerformanceVisualization(BaseVisualization):
    """Team performance visualization showing points by F1 team"""
    
    def __init__(self, parent, controller):
        """
        Initialize the team performance visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        controls_frame = ttk.Frame(self.controls_frame)
        controls_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Select Teams:").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create multi-select listbox with scrollbar
        select_frame = ttk.Frame(controls_frame)
        select_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(select_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.team_listbox = tk.Listbox(select_frame, selectmode=tk.MULTIPLE, 
                                      height=4, width=30, yscrollcommand=scrollbar.set)
        self.team_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.team_listbox.yview)
        
        ttk.Button(controls_frame, text="Update Chart", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Team Performance"
    
    def set_team_options(self, team_options):
        """Set team listbox options
        
        Args:
            team_options (list): List of team option strings
        """
        self.team_listbox.delete(0, tk.END)  # Clear current options
        
        # Add team options to the listbox
        for team in team_options:
            self.team_listbox.insert(tk.END, team)
        
        # Pre-select the top 5 teams
        top_teams = ['RBR', 'FER', 'MER', 'MCL', 'AST']
        for i, team in enumerate(team_options):
            team_id = team.split('(')[-1].rstrip(')')
            if team_id in top_teams:
                self.team_listbox.selection_set(i)
    
    def get_selected_teams(self):
        """Get selected teams
        
        Returns:
            list: List of selected team IDs
        """
        selections = self.team_listbox.curselection()
        if not selections:
            return []
        
        selected_team_items = [self.team_listbox.get(i) for i in selections]
        selected_team_ids = [item.split('(')[-1].rstrip(')') for item in selected_team_items]
        
        return selected_team_ids
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - team_data (list): List of team data dictionaries
                    - team_id (str): Team ID
                    - team_name (str): Team name
                    - race_points (dict): Dictionary mapping race ID to points
                    - total_points (float): Total points across all races
        """
        if not data or not data.get('team_data'):
            self.show_placeholder("No team data available for visualization")
            return
        
        completed_races = data.get('completed_races', [])
        race_dates = data.get('race_dates', {})
        team_data = data.get('team_data', [])
        
        if not completed_races:
            self.show_placeholder("No completed races found")
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(121)  # Line chart for team performance over races
        ax2 = self.figure.add_subplot(122)  # Bar chart for total team points
        
        # Line chart for team performance over races
        for team in team_data:
            team_id = team['team_id']
            team_name = team['team_name']
            points = [team['race_points'].get(race_id, 0) for race_id in completed_races]
            
            ax1.plot(completed_races, points, marker='o', linewidth=2, label=team_name)
        
        # Add race date annotations
        for i, race_id in enumerate(completed_races):
            if i % 2 == 0 and race_id in race_dates:  # Annotate every other race to avoid clutter
                ax1.annotate(f"{race_id}\n{race_dates[race_id]}", 
                           xy=(race_id, 0), 
                           xytext=(0, -25),
                           textcoords='offset points',
                           ha='center', fontsize=8)
        
        # Customize the line chart
        ax1.set_title('Team Performance by Race', fontsize=12)
        ax1.set_xlabel('Race', fontsize=10)
        ax1.set_ylabel('Points', fontsize=10)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)
        
        # Bar chart for total team points
        # Sort by total points
        team_data.sort(key=lambda x: x['total_points'], reverse=True)
        team_names = [t['team_name'] for t in team_data]
        total_points = [t['total_points'] for t in team_data]
        
        # Create horizontal bar chart
        bars = ax2.barh(team_names, total_points)
        
        # Add value annotations
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}', ha='left', va='center', fontsize=9)
        
        # Set team-specific colors if available in the data
        if 'team_colors' in data:
            team_colors = data['team_colors']
            for i, team in enumerate(team_data):
                if team['team_id'] in team_colors:
                    bars[i].set_color(team_colors[team['team_id']])
        
        # Customize the bar chart
        ax2.set_title('Total Team Points', fontsize=12)
        ax2.set_xlabel('Points', fontsize=10)
        ax2.grid(axis='x', alpha=0.3)
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            selected_teams = self.get_selected_teams()
            if selected_teams:
                self.controller.update_visualization(selected_teams)
            else:
                self.show_placeholder("Please select at least one team")