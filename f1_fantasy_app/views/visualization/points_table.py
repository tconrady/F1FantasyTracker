
"""
views/visualization/points_table.py - Points table visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np

class PointsTableVisualization(BaseVisualization):
    """Points table visualization showing driver and player points per race"""
    
    def __init__(self, parent, controller):
        """
        Initialize the points table visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        # Create tab control for different table views
        self.tab_control = ttk.Notebook(self.controls_frame)
        self.tab_control.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.driver_tab = ttk.Frame(self.tab_control)
        self.player_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.driver_tab, text="Driver Points")
        self.tab_control.add(self.player_tab, text="Player Points")
        
        # Driver tab controls
        driver_frame = ttk.Frame(self.driver_tab)
        driver_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(driver_frame, text="Select Driver:").pack(side=tk.LEFT, padx=5, pady=5)
        self.driver_var = tk.StringVar(value="All Drivers")
        self.driver_dropdown = ttk.Combobox(driver_frame, textvariable=self.driver_var, width=30, state="readonly")
        self.driver_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(driver_frame, text="Update Driver Table", 
                  command=lambda: self.on_update_table('driver')).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Player tab controls
        player_frame = ttk.Frame(self.player_tab)
        player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(player_frame, text="Select Player:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player_var = tk.StringVar(value="All Players")
        self.player_dropdown = ttk.Combobox(player_frame, textvariable=self.player_var, width=30, state="readonly")
        self.player_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(player_frame, text="Update Player Table", 
                  command=lambda: self.on_update_table('player')).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Points Table"
    
    def set_driver_options(self, options):
        """Set the options for the driver dropdown
        
        Args:
            options (list): List of driver option strings
        """
        self.driver_dropdown['values'] = options
        
    def set_player_options(self, options):
        """Set the options for the player dropdown
        
        Args:
            options (list): List of player option strings
        """
        self.player_dropdown['values'] = options
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Dictionary containing:
                - table_type (str): 'driver' or 'player'
                - column_labels (list): List of column labels
                - table_data (list): List of row data lists
                - entity_type (str): 'Driver' or 'Player'
        """
        if not data or not data.get('table_data'):
            self.show_placeholder("No data available for visualization")
            return
        
        table_type = data.get('table_type', 'driver')
        column_labels = data.get('column_labels', [])
        table_data = data.get('table_data', [])
        entity_type = data.get('entity_type', 'Driver')
        
        # Clear previous plot
        self.ax.clear()
        self.ax.axis('off')  # Hide axes
        
        # Set up the table
        if table_data:
            # Create the table
            table = self.ax.table(
                cellText=table_data,
                colLabels=column_labels,
                loc='center',
                cellLoc='center'
            )
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)  # Make rows taller
            
            # Adjust column widths
            table.auto_set_column_width(col=list(range(len(column_labels))))
            
            # Set column width for name column
            table.auto_set_column_width([0])
            
            # Add a note about the format
            self.figure.suptitle(
                f"{entity_type} Points Table - Format: Per-Race Points (Cumulative Total)",
                fontsize=14
            )
            
            # Add explanation at the bottom
            self.ax.text(
                0.5, -0.05, 
                "Values shown as 'per-race points (cumulative total)'\n"
                "Per-race points should be the actual points earned in that race.",
                transform=self.ax.transAxes, 
                ha='center', 
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgrey', alpha=0.3)
            )
        else:
            # No data
            self.ax.text(0.5, 0.5, f"No {entity_type.lower()} data found for the selected races",
                       ha='center', va='center', fontsize=12)
        
        # Update canvas
        self.figure.tight_layout()
        self.canvas.draw()
    
    def get_selected_driver(self):
        """Get the selected driver from the dropdown
        
        Returns:
            str: Selected driver or "All Drivers"
        """
        return self.driver_var.get()
    
    def get_selected_player(self):
        """Get the selected player from the dropdown
        
        Returns:
            str: Selected player or "All Players"
        """
        return self.player_var.get()
    
    def on_update_table(self, table_type):
        """Handle update table button click
        
        Args:
            table_type (str): 'driver' or 'player'
        """
        if self.controller:
            self.controller.update_table(table_type)