"""
views/visualizations/credit_efficiency.py - Credit efficiency visualization
"""

from base_visualization import BaseVisualization
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import numpy as np

class CreditEfficiencyVisualization(BaseVisualization):
    """Credit efficiency visualization showing points per credit"""
    
    def __init__(self, parent, controller):
        """
        Initialize the credit efficiency visualization.
        
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
        return "Credit Efficiency"
    
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
                - driver_data (list): List of dictionaries with driver data:
                    - driver_id (str): Driver ID
                    - name (str): Driver name
                    - credits (float): Driver credits
                    - points (float): Driver points
                    - efficiency (float): Points per credit
        """
        if not data or not data.get('driver_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        race_id = data.get('race_id', 'All Races')
        driver_data = data.get('driver_data', [])
        
        # Clear previous plot
        self.fig.clear()
        
        # Create two subplots
        ax1 = self.fig.add_subplot(121)  # Horizontal bar chart for points per credit
        ax2 = self.fig.add_subplot(122)  # Scatter plot for points vs credits
        
        # Sort by efficiency (descending)
        driver_data.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Extract data for horizontal bar chart
        driver_ids = [d['driver_id'] for d in driver_data]
        driver_names = [f"{d['name']} ({d['driver_id']})" for d in driver_data]
        efficiencies = [d['efficiency'] for d in driver_data]
        points = [d['points'] for d in driver_data]
        credits = [d['credits'] for d in driver_data]
        
        # Create horizontal bar chart for efficiency
        y_pos = np.arange(len(driver_ids))
        bars = ax1.barh(y_pos, efficiencies, align='center')
        
        # Color bars by credit tier
        cmap = plt.cm.viridis
        for i, bar in enumerate(bars):
            bar.set_color(cmap(credits[i] / 4))  # Normalize by max credits
        
        # Add value annotations
        for i, v in enumerate(efficiencies):
            ax1.text(v + 0.1, i, f'{v:.2f}', va='center', fontsize=8)
        
        # Customize the horizontal bar chart
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(driver_names, fontsize=8)
        ax1.set_xlabel('Points per Credit', fontsize=10)
        ax1.set_title(f'Driver Efficiency ({race_id})', fontsize=12)
        ax1.grid(axis='x', alpha=0.3)
        
        # Scatter plot for points vs credits
        scatter = ax2.scatter(credits, points, c=efficiencies, cmap='viridis', 
                            s=100, alpha=0.7, edgecolors='black')
        
        # Add driver labels
        for i, driver_id in enumerate(driver_ids):
            ax2.annotate(driver_id, 
                        (credits[i], points[i]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8)
        
        # Add a trend line
        if len(credits) > 1:  # Need at least 2 points for a trend line
            z = np.polyfit(credits, points, 1)
            p = np.poly1d(z)
            ax2.plot([min(credits), max(credits)], [p(min(credits)), p(max(credits))], 
                    "r--", alpha=0.7, label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")
        
        # Add contour lines for equal efficiency
        x_range = np.linspace(min(credits) if credits else 1, max(credits) if credits else 4, 100)
        
        for efficiency in [5, 10, 15, 20]:
            y_vals = efficiency * x_range
            ax2.plot(x_range, y_vals, 'k:', alpha=0.3)
            # Label the contour line in the middle
            mid_x = (min(credits) if credits else 1 + max(credits) if credits else 4) / 2
            mid_y = efficiency * mid_x
            ax2.text(mid_x, mid_y, f'{efficiency} pts/credit', 
                    fontsize=8, alpha=0.7, ha='center', va='bottom')
        
        # Customize the scatter plot
        ax2.set_xlabel('Credits', fontsize=10)
        ax2.set_ylabel('Points', fontsize=10)
        ax2.set_title(f'Points vs Credits ({race_id})', fontsize=12)
        ax2.grid(True, alpha=0.3)
        if len(credits) > 1:
            ax2.legend(fontsize=8)
        
        # Add a colorbar
        cbar = self.fig.colorbar(scatter, ax=ax2)
        cbar.set_label('Points per Credit', fontsize=10)
        
        # Note about theoretical data if needed
        if data.get('is_theoretical', False):
            self.fig.text(0.5, 0.01, 
                         "Note: Using theoretical data based on driver credits (no race results yet).",
                         ha='center', fontsize=9, style='italic')
        
        # Improve layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        if self.controller:
            selected_race = self.race_var.get()
            self.controller.update_visualization(selected_race)