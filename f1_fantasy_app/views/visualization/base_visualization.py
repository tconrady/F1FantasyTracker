"""
views/visualization/base_visualization.py - Base class for visualizations
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class BaseVisualization:
    """Base class for all visualizations"""
    
    def __init__(self, parent, controller):
        """
        Initialize the base visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        self.parent = parent
        self.controller = controller
        self.figure = None
        self.canvas = None
        
        # Create frame for controls
        self.controls_frame = ttk.Frame(parent)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create frame for the visualization
        self.viz_frame = ttk.LabelFrame(parent, text=self.get_title())
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure and canvas
        self.create_figure()
        
    def create_figure(self):
        """Create the matplotlib figure and canvas"""
        self.figure = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create default axes
        self.ax = self.figure.add_subplot(111)
        
        # Show placeholder
        self.show_placeholder("Select options to show visualization")
        
    def get_title(self):
        """Get the title for this visualization
        
        Returns:
            str: Visualization title
        """
        return "Visualization"
    
    def show_placeholder(self, message):
        """Show a placeholder message
        
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
        
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data: Data for the visualization
        """
        pass
    
    def clear(self):
        """Clear the visualization"""
        self.ax.clear()
        self.canvas.draw()