"""
views/visualizations/player_driver_points.py - Player driver points visualization
"""

from base_visualization import BaseVisualization
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import numpy as np

class PlayerDriverPointsVisualization(BaseVisualization):
    """Visualization showing driver points contribution for each player"""
    
    def __init__(self, parent, controller):
        """
        Initialize the player driver points visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        ttk.Label(self.controls_frame, text="Select Race:").pack(side=tk.LEFT, padx=5, pady=5)
        self.race_var = tk.StringVar(value="All Races")
        self.race_dropdown = ttk.Combobox(self.controls_frame, textvariable=self.race_var, state="readonly")
        self.race_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(self.controls_frame, text="Update Chart", 
                  command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Driver Points by Player"
    
    def set_race_options(self, race_options):
        """Set the options for the race dropdown
        
        Args:
            race_options (list): List of race option strings
        """
        # Add "All Races" option
        options = ["All Races"] + race_options
        self.race_dropdown['values'] = options
        self.race_dropdown.current(0)  # Default to "All Races"
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Dictionary containing:
                - race_id (str): Race ID or "All Races"
                - player_data (list): List of dictionaries with player data:
                    - player (str): Player name
                    - driver1 (dict): First driver data
                      - id (str): Driver ID
                      - name (str): Driver name
                      - points (float): Driver points
                    - driver2 (dict): Second driver data
                      - id (str): Driver ID
                      - name (str): Driver name
                      - points (float): Driver points
                    - totalPoints (float): Total points
        """
        if not data or not data.get('player_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        race_id = data.get('race_id', 'All Races')
        player_data = data.get('player_data', [])
        
        # Clear previous plot
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Set up display
        bar_width = 0.6
        positions = np.arange(len(player_data))
        
        # Define colors
        colors = {
            'driver1_pos': '#3B82F6',  # Blue
            'driver1_neg': '#93C5FD',  # Light blue
            'driver2_pos': '#EF4444',  # Red
            'driver2_neg': '#FCA5A5',  # Light red
            'total': '#4F46E5'         # Purple
        }
        
        # Create bars for each player
        for i, player in enumerate(player_data):
            driver1_points = player['driver1']['points']
            driver2_points = player['driver2']['points']
            total_points = player['totalPoints']
            
            # CASE 1: Both drivers positive
            if driver1_points >= 0 and driver2_points >= 0:
                # Driver 1 (bottom)
                bar1 = ax.bar(positions[i], driver1_points, bar_width, 
                            bottom=0, color=colors['driver1_pos'], 
                            edgecolor='black', linewidth=0.5)
                
                # Add driver1 label if enough space
                if driver1_points > 5:
                    ax.text(positions[i], driver1_points/2, player['driver1']['id'],
                          ha='center', va='center', color='white', fontweight='bold')
                
                # Driver 2 (top)
                bar2 = ax.bar(positions[i], driver2_points, bar_width, 
                            bottom=driver1_points, color=colors['driver2_pos'], 
                            edgecolor='black', linewidth=0.5)
                
                # Add driver2 label if enough space
                if driver2_points > 5:
                    ax.text(positions[i], driver1_points + driver2_points/2, player['driver2']['id'],
                          ha='center', va='center', color='white', fontweight='bold')
            
            # CASE 2: Mixed with positive total
            elif total_points > 0:
                # Determine which driver is positive and which is negative
                pos_driver = player['driver1'] if driver1_points > 0 else player['driver2']
                neg_driver = player['driver2'] if driver2_points < 0 else player['driver1']
                
                # Positive bar (matching total height)
                pos_bar = ax.bar(positions[i], total_points, bar_width, 
                                bottom=0, 
                                color=colors['driver1_pos'] if pos_driver == player['driver1'] else colors['driver2_pos'],
                                edgecolor='black', linewidth=0.5)
                
                # Add positive driver label
                if total_points > 5:
                    ax.text(positions[i], total_points/2, pos_driver['id'],
                          ha='center', va='center', color='white', fontweight='bold')
                
                # Add negative bar below 0
                neg_height = abs(neg_driver['points'])
                neg_bar = ax.bar(positions[i], -neg_height, bar_width, 
                                bottom=0, 
                                color=colors['driver1_neg'] if neg_driver == player['driver1'] else colors['driver2_neg'],
                                edgecolor='black', linewidth=0.5, 
                                hatch='///', alpha=0.8)
                
                # Add relationship label showing subtraction to negative bar
                if neg_height > 5:
                    ax.text(positions[i], -neg_height/2, f"{pos_driver['id']} - {neg_driver['id']}",
                          ha='center', va='center', color='black', fontweight='bold')
            
            # CASE 3: Negative total (both negative or mixed with negative total)
            else:
                # Draw a dashed border from 0 to total
                rect = plt.Rectangle((positions[i] - bar_width/2, 0), bar_width, total_points, 
                                    fill=False, linestyle='--', edgecolor='black')
                ax.add_patch(rect)
                
                # If both drivers are negative
                if driver1_points <= 0 and driver2_points <= 0:
                    # First negative driver
                    neg1_height = abs(driver1_points)
                    neg1_bar = ax.bar(positions[i], -neg1_height, bar_width, 
                                    bottom=0, 
                                    color=colors['driver1_neg'],
                                    edgecolor='black', linewidth=0.5, 
                                    hatch='///', alpha=0.8)
                    
                    # Add driver1 label
                    if neg1_height > 5:
                        ax.text(positions[i], -neg1_height/2, player['driver1']['id'],
                              ha='center', va='center', color='black', fontweight='bold')
                    
                    # Second negative driver
                    neg2_height = abs(driver2_points)
                    neg2_bar = ax.bar(positions[i], -neg2_height, bar_width, 
                                    bottom=-neg1_height, 
                                    color=colors['driver2_neg'],
                                    edgecolor='black', linewidth=0.5, 
                                    hatch='///', alpha=0.8)
                    
                    # Add driver2 label
                    if neg2_height > 5:
                        ax.text(positions[i], -neg1_height - neg2_height/2, player['driver2']['id'],
                              ha='center', va='center', color='black', fontweight='bold')
                
                # If mixed with negative total (negative > positive)
                else:
                    pos_driver = player['driver1'] if driver1_points > 0 else player['driver2']
                    neg_driver = player['driver2'] if driver2_points < 0 else player['driver1']
                    
                    pos_height = abs(pos_driver['points'])
                    neg_height = abs(neg_driver['points'])
                    
                    # Draw the negative bar from total to total+remainder
                    remainder = neg_height - pos_height
                    
                    if remainder > 0:
                        neg_bar = ax.bar(positions[i], -remainder, bar_width, 
                                      bottom=total_points, 
                                      color=colors['driver1_neg'] if neg_driver == player['driver1'] else colors['driver2_neg'],
                                      edgecolor='black', linewidth=0.5, 
                                      hatch='///', alpha=0.8)
                        
                        # Add relationship label showing subtraction
                        if remainder > 5:
                            ax.text(positions[i], total_points - remainder/2, f"{pos_driver['id']} - {neg_driver['id']}",
                                  ha='center', va='center', color='black', fontweight='bold')
            
            # Add total points label
            if total_points >= 0:
                ax.text(positions[i], total_points + 1, f"{total_points:.1f}", 
                      ha='center', va='bottom', color=colors['total'], fontweight='bold')
            else:
                ax.text(positions[i], total_points - 1, f"{total_points:.1f}", 
                      ha='center', va='top', color=colors['total'], fontweight='bold')
        
        # Set up axes and labels
        ax.set_xticks(positions)
        ax.set_xticklabels([p['player'] for p in player_data], rotation=0, fontweight='bold')
        
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        
        # Format y-axis to show actual values
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}"))
        
        # Set proper axis labels and title
        ax.set_ylabel('Points', fontsize=10)
        title = f'F1 Fantasy: Driver Points Contribution by Player\n{race_id}'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        # Create legend with custom patches
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=colors['driver1_pos'], label='Driver 1'),
            Patch(facecolor=colors['driver2_pos'], label='Driver 2'),
            Patch(facecolor=colors['driver1_neg'], hatch='///', label='Negative contribution')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Add annotation
        ax.text(0.5, -0.15, "Driver IDs are shown on the bars.", 
              ha='center', va='center', transform=ax.transAxes, fontsize=10, color='gray')
        
        # Ensure axes display correctly with proper spacing
        plt.subplots_adjust(bottom=0.18, left=0.12, right=0.92, top=0.88)
        
        # Get current y limits and ensure they're appropriate
        y_min, y_max = ax.get_ylim()
        # Set reasonable y limits with padding
        ax.set_ylim(min(y_min, -15), max(y_max * 1.1, 5))
        
        # Update the plot
        self.fig.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            selected_race = self.race_var.get()
            self.controller.update_visualization(selected_race)