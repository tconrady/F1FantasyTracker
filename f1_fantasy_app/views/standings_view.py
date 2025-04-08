"""
views/standings_view.py - View for standings display
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.base_view import BaseView

class StandingsView(BaseView):
    """View for standings display, showing league standings and race breakdowns"""
    
    def __init__(self, parent):
        """
        Initialize the standings view.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        
        # Split into top and bottom frames
        self.top_frame = ttk.Frame(self.frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.bottom_frame = ttk.Frame(self.frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set up controls
        self.setup_controls()
        
        # Set up visualization area
        self.setup_visualization()
    
    def setup_controls(self):
        """Set up the controls for the standings view"""
        controls_frame = ttk.LabelFrame(self.top_frame, text="Visualization Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Show Season Standings", 
                  command=self.on_show_standings).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Select Race:").pack(side=tk.LEFT, padx=5, pady=5)
        self.race_var = tk.StringVar()
        self.race_dropdown = ttk.Combobox(controls_frame, textvariable=self.race_var, state="readonly")
        self.race_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Show Race Breakdown", 
                  command=self.on_show_race_breakdown).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add a refresh button
        ttk.Button(controls_frame, text="Refresh Data", 
                  command=self.on_refresh_data).pack(side=tk.RIGHT, padx=5, pady=5)
    
    def setup_visualization(self):
        """Set up the visualization area"""
        viz_frame = ttk.LabelFrame(self.bottom_frame, text="Standings Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure and canvas
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create default axes
        self.ax = self.figure.add_subplot(111)
        
        # Show placeholder
        self.show_placeholder("Select an option above to visualize standings")
    
    def show_placeholder(self, message):
        """Show a placeholder message in the visualization area
        
        Args:
            message (str): Message to display
        """
        self.ax.clear()
        self.ax.text(0.5, 0.5, message, 
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=14)
        self.ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def set_race_options(self, race_options):
        """Set the options for the race dropdown
        
        Args:
            race_options (list): List of race option strings
        """
        self.race_dropdown['values'] = race_options
        
        # Select the most recent race if available
        if race_options:
            self.race_dropdown.current(len(race_options) - 1)
    
    def get_selected_race(self):
        """Get the selected race from the dropdown
        
        Returns:
            str: Selected race or empty string
        """
        return self.race_var.get()
    
    def show_season_standings(self, standings_data):
        """Show the season standings visualization
        
        Args:
            standings_data (dict): Data for the standings visualization
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - player_data (list): List of player data dictionaries
                    - player_id (str): Player ID
                    - player_name (str): Player name
                    - cumulative_points (list): List of cumulative points by race
        """
        # Clear previous plot
        self.ax.clear()
        
        completed_races = standings_data.get('completed_races', [])
        race_dates = standings_data.get('race_dates', {})
        player_data = standings_data.get('player_data', [])
        
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
                self.ax.annotate(f"{race_id}\n{race_dates.get(race_id, '')}", 
                               xy=(race_id, 0), 
                               xytext=(0, -25),
                               textcoords='offset points',
                               ha='center', fontsize=8)
        
        # Add final points values
        for player in player_data:
            if player['cumulative_points']:
                final_points = player['cumulative_points'][-1]
                self.ax.annotate(f"{final_points:.1f}", 
                               xy=(completed_races[-1], final_points),
                               xytext=(5, 0),
                               textcoords='offset points',
                               fontsize=9, fontweight='bold')
        
        # Update the plot
        self.figure.tight_layout()
        self.canvas.draw()
    
    def show_race_breakdown(self, breakdown_data):
        """Show the race breakdown visualization
        
        Args:
            breakdown_data (dict): Data for the race breakdown
                - race_id (str): Race ID
                - race_name (str): Race name
                - player_results (list): List of player result dictionaries
                    - player_id (str): Player ID
                    - player_name (str): Player name
                    - points (float): Points scored in the race
                    - calculation_details (str): Point calculation details
        """
        # Clear previous plot
        self.ax.clear()
        
        race_id = breakdown_data.get('race_id', '')
        race_name = breakdown_data.get('race_name', '')
        player_results = breakdown_data.get('player_results', [])
        
        # Sort by points (descending)
        player_results.sort(key=lambda x: x['points'], reverse=True)
        
        # Extract data for plotting
        player_names = [result['player_name'] for result in player_results]
        points = [result['points'] for result in player_results]
        
        # Create bar chart
        bars = self.ax.bar(player_names, points)
        
        # Add point values above bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width()/2., 
                height + 0.5, 
                f'{height:.1f}', 
                ha='center', 
                va='bottom'
            )
        
        # Formatting
        self.ax.set_title(f'F1 Fantasy Points for {race_name} ({race_id})', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Player', fontsize=12)
        self.ax.set_ylabel('Points', fontsize=12)
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid(axis='y', alpha=0.3)
        
        # Update the plot
        self.figure.tight_layout()
        self.canvas.draw()
    
    # Event handlers - to be overridden by controller
    def on_show_standings(self):
        """Handle show standings button click"""
        pass
    
    def on_show_race_breakdown(self):
        """Handle show race breakdown button click"""
        pass
    
    def on_refresh_data(self):
        """Handle refresh data button click"""
        pass