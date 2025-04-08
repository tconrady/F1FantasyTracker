"""
views/visualization/credit_efficiency.py - Credit efficiency visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

class CreditEfficiencyVisualization(BaseVisualization):
    """Credit efficiency visualization (points per credit)"""
    
    def __init__(self, parent, controller):
        """
        Initialize the credit efficiency visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        race_frame = ttk.Frame(self.controls_frame)
        race_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(race_frame, text="Select Race:").pack(side=tk.LEFT, padx=5, pady=5)
        self.race_var = tk.StringVar(value="All Races")
        self.race_dropdown = ttk.Combobox(race_frame, textvariable=self.race_var, state="readonly")
        self.race_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(race_frame, text="Update Chart", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Note label for simulation mode
        self.note_var = tk.StringVar()
        self.note_label = ttk.Label(self.controls_frame, textvariable=self.note_var, foreground="blue")
        self.note_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Credit Efficiency"
    
    def set_race_options(self, race_options):
        """Set race dropdown options
        
        Args:
            race_options (list): List of race options
        """
        options = ["All Races"] + race_options
        self.race_dropdown['values'] = options
        self.race_dropdown.current(0)  # Default to "All Races"
    
    def get_selected_race(self):
        """Get selected race
        
        Returns:
            str: Selected race ID or "All Races"
        """
        selection = self.race_var.get()
        if selection == "All Races":
            return selection
            
        # Extract race ID
        return selection.split('-')[0].strip()
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - race_id (str): Selected race ID or "All Races"
                - is_theoretical (bool): Whether this is theoretical data
                - note (str): Note about data source
                - driver_data (list): List of driver efficiency data dicts
                - total_races (int): Total races considered
        """
        if not data or not data.get('driver_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        race_id = data.get('race_id', "All Races")
        is_theoretical = data.get('is_theoretical', False)
        note = data.get('note', "")
        driver_data = data.get('driver_data', [])
        
        # Display note if provided
        if note:
            self.note_var.set(note)
            self.note_label.pack(side=tk.LEFT, padx=10, pady=5)
        else:
            self.note_label.pack_forget()
        
        # Clear previous plot
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(121)  # Horizontal bar chart
        ax2 = self.figure.add_subplot(122)  # Scatter plot
        
        # Sort by efficiency
        driver_data.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Prepare data for horizontal bar chart
        driver_ids = [d['driver_id'] for d in driver_data]
        driver_names = [d['name'] for d in driver_data]
        efficiencies = [d['efficiency'] for d in driver_data]
        avg_points = [d['avg_points'] for d in driver_data]
        credits = [d['credits'] for d in driver_data]
        
        # Create horizontal bar chart for efficiency
        y_pos = np.arange(len(driver_ids))
        bars = ax1.barh(y_pos, efficiencies, align='center')
        
        # Color bars by credit tier
        cmap = plt.get_cmap('viridis')
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
        scatter = ax2.scatter(credits, avg_points, c=efficiencies, cmap='viridis', 
                            s=100, alpha=0.7, edgecolors='black')
        
        # Add driver labels
        for i, driver_id in enumerate(driver_ids):
            ax2.annotate(driver_id, 
                        (credits[i], avg_points[i]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8)
        
        # Add a trend line
        z = np.polyfit(credits, avg_points, 1)
        p = np.poly1d(z)
        ax2.plot([min(credits), max(credits)], [p(min(credits)), p(max(credits))], 
                "r--", alpha=0.7, label=f"Trend: y={z[0]:.2f}x+{z[1]:.2f}")
        
        # Add contour lines for equal efficiency
        x_range = np.linspace(min(credits), max(credits), 100)
        
        for efficiency in [5, 10, 15, 20]:
            y_vals = efficiency * x_range
            ax2.plot(x_range, y_vals, 'k:', alpha=0.3)
            # Label the contour line in the middle
            mid_x = (min(credits) + max(credits)) / 2