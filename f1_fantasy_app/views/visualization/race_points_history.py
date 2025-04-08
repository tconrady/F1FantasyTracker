"""
views/visualization/race_points_history.py - Race points history visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class RacePointsHistoryVisualization(BaseVisualization):
    """Race points history visualization showing distribution of points across races"""
    
    def __init__(self, parent, controller):
        """
        Initialize the race points history visualization.
        
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
        return "Race Points History"
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - race_results (list): List of race result data
                - box_data (list): List of lists with points data for each race for boxplot
                - violin_data (pd.DataFrame): DataFrame for violin plot
        """
        if not data or not data.get('completed_races'):
            self.show_placeholder("No completed races found")
            return
        
        completed_races = data.get('completed_races', [])
        race_dates = data.get('race_dates', {})
        box_data = data.get('box_data', [])
        violin_data = data.get('violin_data', pd.DataFrame())
        
        if not box_data:
            self.show_placeholder("No race points data available")
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Create two subplots
        ax1 = self.figure.add_subplot(121)  # Boxplot by race
        ax2 = self.figure.add_subplot(122)  # Violin plot
        
        # Create boxplot
        box = ax1.boxplot(box_data, patch_artist=True, notch=True)
        
        # Customize boxplot colors
        for patch in box['boxes']:
            patch.set_facecolor('lightblue')
        
        # Customize the boxplot
        ax1.set_xticks(range(1, len(completed_races) + 1))
        ax1.set_xticklabels(completed_races, rotation=45)
        ax1.set_ylabel('Points', fontsize=10)
        ax1.set_title('Points Distribution by Race', fontsize=12)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add race dates as annotations
        for i, race_id in enumerate(completed_races):
            if race_id in race_dates:
                ax1.annotate(f"{race_dates[race_id]}", 
                           xy=(i+1, 0), 
                           xytext=(0, -25),
                           textcoords='offset points',
                           ha='center', fontsize=8, rotation=45)
        
        # Create violin plot if data is available
        if not violin_data.empty:
            # Create violin plot
            sns.violinplot(x='Race', y='Points', data=violin_data, ax=ax2, 
                          inner='quartile', palette='Blues')
            
            # Set ticks before labels
            ax2.set_xticks(range(len(completed_races)))
            ax2.set_xticklabels(completed_races, rotation=45)
            ax2.set_ylabel('Points', fontsize=10)
            ax2.set_title('Points Density by Race', fontsize=12)
            ax2.grid(axis='y', alpha=0.3)
            
            # Add race date annotations
            for i, race_id in enumerate(completed_races):
                if race_id in race_dates:
                    ax2.annotate(f"{race_dates[race_id]}", 
                               xy=(i, 0), 
                               xytext=(0, -25),
                               textcoords='offset points',
                               ha='center', fontsize=8, rotation=45)
            
            # Add statistics annotations
            if 'statistics' in data:
                stats = data['statistics']
                for i, race_id in enumerate(completed_races):
                    if race_id in stats:
                        mean = stats[race_id]['mean']
                        median = stats[race_id]['median']
                        
                        ax2.annotate(f"μ={mean:.1f}", 
                                   xy=(i, mean),
                                   xytext=(5, 0),
                                   textcoords="offset points",
                                   fontsize=8, fontweight='bold', color='red')
                        
                        ax2.annotate(f"m={median:.1f}", 
                                   xy=(i, median),
                                   xytext=(-25, 0),
                                   textcoords="offset points",
                                   fontsize=8, fontweight='bold', color='blue')
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            self.controller.update_visualization()