"""
views/visualization/points_breakdown.py - Points breakdown visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

class PointsBreakdownVisualization(BaseVisualization):
    """Points breakdown visualization showing driver contributions for each player"""
    
    def __init__(self, parent, controller):
        """
        Initialize the points breakdown visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        player_frame = ttk.Frame(self.controls_frame)
        player_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(player_frame, text="Select Player:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player_var = tk.StringVar()
        self.player_dropdown = ttk.Combobox(player_frame, textvariable=self.player_var, state="readonly")
        self.player_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(player_frame, text="Update Chart", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Points Breakdown"
    
    def set_player_options(self, player_options):
        """Set player dropdown options
        
        Args:
            player_options (list): List of player option strings
        """
        self.player_dropdown['values'] = player_options
        if player_options:
            self.player_dropdown.current(0)
    
    def get_selected_player(self):
        """Get selected player
        
        Returns:
            str: Selected player ID or empty string
        """
        selection = self.player_var.get()
        if not selection:
            return ""
            
        # Extract player ID
        if '(' in selection and ')' in selection:
            return selection.split('(')[-1].split(')')[0]
        return selection
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - player_name (str): Player name
                - has_negative (bool): Whether there are negative point values
                - driver_points (dict): Dictionary mapping driver IDs to their points
                - driver_names (dict): Dictionary mapping driver IDs to their names
                - completed_races (list): List of completed race IDs
                - race_points (dict): Dictionary mapping race IDs to driver point dictionaries
        """
        if not data:
            self.show_placeholder("No data available for visualization")
            return
        
        player_name = data.get('player_name', '')
        has_negative = data.get('has_negative', False)
        driver_points = data.get('driver_points', {})
        driver_names = data.get('driver_names', {})
        completed_races = data.get('completed_races', [])
        race_points = data.get('race_points', {})
        
        if not driver_points:
            self.show_placeholder(f"No point breakdown data available for {player_name}")
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(121)  # Pie or bar chart for overall contribution
        ax2 = self.figure.add_subplot(122)  # Bar chart for race breakdown
        
        # Prepare data for charts
        labels = list(driver_points.keys())
        sizes = list(driver_points.values())
        
        # Check if we have any negative values
        if has_negative:
            # Create horizontal bar chart for overall contribution
            sorted_indices = sorted(range(len(sizes)), key=lambda i: abs(sizes[i]), reverse=True)
            sorted_labels = [labels[i] for i in sorted_indices]
            sorted_sizes = [sizes[i] for i in sorted_indices]
            sorted_names = [driver_names.get(labels[i], labels[i]) for i in sorted_indices]
            
            # Colors - blue for positive, red for negative
            colors = ['royalblue' if size >= 0 else 'tomato' for size in sorted_sizes]
            
            # Create horizontal bar chart
            bars = ax1.barh(sorted_names, sorted_sizes, color=colors)
            
            # Add values to bars
            for bar in bars:
                width = bar.get_width()
                x_pos = width + 0.5 if width >= 0 else width - 0.5
                ax1.annotate(f'{width:.1f}',
                            xy=(x_pos, bar.get_y() + bar.get_height()/2),
                            ha='left' if width >= 0 else 'right', 
                            va='center',
                            fontsize=9,
                            fontweight='bold')
            
            ax1.set_title(f'Driver Contribution for {player_name}', fontsize=12)
            ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)  # Add a vertical line at 0
            ax1.grid(axis='x', alpha=0.3)
        else:
            # Pie chart for positive-only values
            wedges, _, autotexts = ax1.pie(
                sizes, 
                labels=None,
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.tab10.colors[:len(labels)]
            )
            
            # Add legend
            legend_labels = [f"{driver_names.get(driver_id, driver_id)}: {points:.1f} pts" 
                        for driver_id, points in zip(labels, sizes)]
            ax1.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(-0.1, 0.5), fontsize=9)
            ax1.set_title(f'Driver Contribution for {player_name}', fontsize=12)
        
        # Bar chart for race points
        if completed_races and race_points:
            drivers = list(driver_points.keys())
            x = np.arange(len(completed_races))
            width = 0.8 / len(drivers)
            
            for i, driver_id in enumerate(drivers):
                driver_race_points = [race_points.get(race_id, {}).get(driver_id, 0) for race_id in completed_races]
                offset = width * i - width * len(drivers) / 2 + width / 2
                
                bars = ax2.bar(x + offset, driver_race_points, width, 
                            label=driver_names.get(driver_id, driver_id),
                            color=plt.cm.tab10.colors[i % 10])
                
                # Add point values on bars
                for bar in bars:
                    height = bar.get_height()
                    ax2.annotate(f'{height:.1f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, rotation=90)
            
            ax2.set_title(f'Points by Race for {player_name}', fontsize=12)
            ax2.set_xticks(x)
            ax2.set_xticklabels(completed_races, rotation=45)
            ax2.set_ylabel('Points', fontsize=10)
            ax2.grid(axis='y', alpha=0.3)
            ax2.legend(fontsize=9)
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            selected_player = self.get_selected_player()
            self.controller.update_visualization(selected_player)