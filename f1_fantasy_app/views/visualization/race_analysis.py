"""
views/visualization/race_analysis.py - Race analysis dashboard
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

class RaceAnalysisVisualization(BaseVisualization):
    """Race analysis dashboard showing various performance metrics for a race"""
    
    def __init__(self, parent, controller):
        """
        Initialize the race analysis visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        controls_frame = ttk.Frame(self.controls_frame)
        controls_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Select Race:").pack(side=tk.LEFT, padx=5, pady=5)
        self.race_var = tk.StringVar()
        self.race_dropdown = ttk.Combobox(controls_frame, textvariable=self.race_var, state="readonly")
        self.race_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Analysis View:").pack(side=tk.LEFT, padx=5, pady=5)
        self.view_var = tk.StringVar(value="Performance Summary")
        self.view_dropdown = ttk.Combobox(controls_frame, textvariable=self.view_var, state="readonly",
                                       values=["Performance Summary", "Fantasy Impact Events", "Player Standings Impact"])
        self.view_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Update Analysis", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Race Analysis"
    
    def set_race_options(self, race_options):
        """Set race dropdown options
        
        Args:
            race_options (list): List of race option strings
        """
        self.race_dropdown['values'] = race_options
        if race_options:
            self.race_dropdown.current(len(race_options) - 1)  # Default to most recent race
    
    def get_selected_race(self):
        """Get selected race
        
        Returns:
            str: Selected race ID or empty string
        """
        selection = self.race_var.get()
        if not selection:
            return ""
            
        # Extract race ID
        return selection.split('-')[0].strip()
    
    def get_selected_view(self):
        """Get selected analysis view
        
        Returns:
            str: Selected view type
        """
        return self.view_var.get()
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - race_id (str): Race ID
                - race_name (str): Race name
                - view_type (str): Analysis view type
                - view_data (dict): View-specific data
        """
        if not data:
            self.show_placeholder("No data available for visualization")
            return
        
        race_id = data.get('race_id', '')
        race_name = data.get('race_name', '')
        view_type = data.get('view_type', '')
        view_data = data.get('view_data', {})
        
        if not race_id or not view_type:
            self.show_placeholder("Please select a race and analysis view")
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Handle different view types
        if view_type == "Performance Summary":
            self.show_performance_summary(race_id, race_name, view_data)
        elif view_type == "Fantasy Impact Events":
            self.show_fantasy_impact_events(race_id, race_name, view_data)
        elif view_type == "Player Standings Impact":
            self.show_player_standings_impact(race_id, race_name, view_data)
        else:
            self.show_placeholder(f"Unknown view type: {view_type}")
        
        # Improve layout
        self.figure.tight_layout(rect=[0, 0, 1, 0.95])  # Leave room for suptitle
        self.canvas.draw()
    
    def show_performance_summary(self, race_id, race_name, data):
        """Show performance summary visualization
        
        Args:
            race_id (str): Race ID
            race_name (str): Race name
            data (dict): Performance summary data
        """
        # Create GridSpec for flexible layout
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1])
        
        # Top left - Overall driver performance
        ax1 = self.figure.add_subplot(gs[0, 0])
        
        # Get driver performance data
        driver_data = data.get('driver_performance', [])
        
        if driver_data:
            # Sort by points (best at the top)
            driver_data.sort(key=lambda x: x['points'], reverse=True)
            
            # Take top drivers (limit to 10 for readability)
            top_drivers = driver_data[:10]
            driver_names = [d['name'] for d in top_drivers]
            driver_points = [d['points'] for d in top_drivers]
            
            # Create horizontal bar chart
            bars = ax1.barh(driver_names, driver_points)
            
            # Color bars by point value
            cmap = plt.cm.Blues
            normalized_points = [(p - min(driver_points)) / (max(driver_points) - min(driver_points) + 0.1) 
                              for p in driver_points]
            for i, bar in enumerate(bars):
                bar.set_color(cmap(0.3 + 0.7 * normalized_points[i]))
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{width:.1f}", ha='left', va='center', fontsize=9)
            
            ax1.set_title(f'Top Driver Fantasy Points', fontsize=11)
            ax1.grid(axis='x', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "No driver performance data available",
                   ha='center', va='center', transform=ax1.transAxes)
            ax1.axis('off')
        
        # Top right - Player performance
        ax2 = self.figure.add_subplot(gs[0, 1])
        
        # Get player performance data
        player_data = data.get('player_performance', [])
        
        if player_data:
            # Sort by points (best at the top)
            player_data.sort(key=lambda x: x['points'], reverse=True)
            
            player_names = [p['name'] for p in player_data]
            player_points = [p['points'] for p in player_data]
            
            # Create horizontal bar chart
            bars = ax2.barh(player_names, player_points)
            
            # Color bars by position
            cmap = plt.cm.Greens
            normalized_pos = [(len(player_names) - i) / len(player_names) for i in range(len(player_names))]
            for i, bar in enumerate(bars):
                bar.set_color(cmap(0.3 + 0.7 * normalized_pos[i]))
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{width:.1f}", ha='left', va='center', fontsize=9)
            
            ax2.set_title(f'Player Performance', fontsize=11)
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No player performance data available",
                   ha='center', va='center', transform=ax2.transAxes)
            ax2.axis('off')
        
        # Bottom left - Driver performance vs season average
        ax3 = self.figure.add_subplot(gs[1, 0])
        
        # Get driver delta data
        driver_deltas = data.get('driver_deltas', [])
        
        if driver_deltas:
            # Sort by absolute delta (largest first)
            driver_deltas.sort(key=lambda x: abs(x['delta']), reverse=True)
            
            # Take top performers/underperformers
            top_deltas = driver_deltas[:8]  # Limit to 8 for readability
            driver_names = [d['name'] for d in top_deltas]
            deltas = [d['delta'] for d in top_deltas]
            
            # Create horizontal bar chart
            bars = ax3.barh(driver_names, deltas)
            
            # Color bars by delta (positive = green, negative = red)
            for i, bar in enumerate(bars):
                bar.set_color('forestgreen' if deltas[i] >= 0 else 'crimson')
            
            # Add zero line
            ax3.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                x_pos = width + 0.5 if width >= 0 else width - 0.5
                ax3.annotate(f'{width:+.1f}',
                            xy=(x_pos, bar.get_y() + bar.get_height()/2),
                            ha='left' if width >= 0 else 'right', 
                            va='center',
                            fontsize=9,
                            fontweight='bold')
            
            ax3.set_title(f'Performance vs. Season Average', fontsize=11)
            ax3.grid(axis='x', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, "No previous races to compare",
                   ha='center', va='center', transform=ax3.transAxes)
            ax3.axis('off')
        
        # Bottom right - Dramatic points
        ax4 = self.figure.add_subplot(gs[1, 1])
        
        # Get impactful driver data
        impactful_drivers = data.get('impactful_drivers', [])
        
        if impactful_drivers:
            # Sort by absolute impact points (smallest first for better display)
            impactful_drivers.sort(key=lambda x: abs(x['points']), reverse=False)
            
            # Format for display
            labels = [f"{p['player_name']}: {p['driver_name']} ({p['driver_id']})" for p in impactful_drivers]
            values = [p['points'] for p in impactful_drivers]
            
            # Create horizontal bar chart
            bars = ax4.barh(labels, values)
            
            # Color bars by value
            for i, bar in enumerate(bars):
                bar.set_color('forestgreen' if values[i] >= 0 else 'crimson')
            
            # Add zero line
            ax4.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                x_pos = width + 0.5 if width >= 0 else width - 0.5
                ax4.annotate(f'{width:+.1f}',
                            xy=(x_pos, bar.get_y() + bar.get_height()/2),
                            ha='left' if width >= 0 else 'right', 
                            va='center',
                            fontsize=9,
                            fontweight='bold')
            
            ax4.set_title(f'Most Impactful Driver Performances', fontsize=11)
            ax4.grid(axis='x', alpha=0.3)
        else:
            ax4.text(0.5, 0.5, "No impactful driver data available",
                   ha='center', va='center', transform=ax4.transAxes)
            ax4.axis('off')
        
        # Add overall title
        self.figure.suptitle(f'Race Analysis: {race_name}', fontsize=14, fontweight='bold')
    
    def show_fantasy_impact_events(self, race_id, race_name, data):
        """Show fantasy impact events visualization
        
        Args:
            race_id (str): Race ID
            race_name (str): Race name
            data (dict): Fantasy impact event data
        """
        # Create a figure with 2x2 layout
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1])
        
        # Top left: Best value drivers
        ax1 = self.figure.add_subplot(gs[0, 0])
        
        # Get best value drivers data
        best_value_drivers = data.get('best_value_drivers', [])
        
        if best_value_drivers:
            # Sort by efficiency (best at top)
            best_value_drivers.sort(key=lambda x: x['efficiency'], reverse=False)
            
            # Format for display
            labels = [f"{d['name']} ({d['driver_id']}) - {d['credits']} credits" for d in best_value_drivers]
            values = [d['efficiency'] for d in best_value_drivers]
            
            # Create horizontal bar chart
            bars = ax1.barh(labels, values)
            
            # Color bars by value
            cmap = plt.cm.Blues
            min_value = min(values) if values else 0
            max_value = max(values) if values else 1
            value_range = max_value - min_value
            
            for i, bar in enumerate(bars):
                normalized_value = (values[i] - min_value) / (value_range + 0.1)
                bar.set_color(cmap(0.3 + 0.7 * normalized_value))
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                        f"{width:.2f} pts/credit", ha='left', va='center', fontsize=8)
            
            # Set consistent x-axis limits
            ax1.set_xlim(0, data.get('value_scale_max', 17))
            
            ax1.set_title(f'Best Value Drivers', fontsize=11)
            ax1.grid(axis='x', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "No value driver data available",
                   ha='center', va='center', transform=ax1.transAxes)
            ax1.axis('off')
        
        # Top right: Underperforming drivers
        ax2 = self.figure.add_subplot(gs[0, 1])
        
        # Get underperforming drivers data
        underperforming_drivers = data.get('underperforming_drivers', [])
        
        if underperforming_drivers:
            # Sort by efficiency (worst at top)
            underperforming_drivers.sort(key=lambda x: x['efficiency'])
            
            # Format for display
            labels = [f"{d['name']} ({d['driver_id']}) - {d['credits']} credits" for d in underperforming_drivers]
            values = [d['efficiency'] for d in underperforming_drivers]
            
            # Create horizontal bar chart
            bars = ax2.barh(labels, values)
            
            # Color bars by value
            for i, bar in enumerate(bars):
                if values[i] < 0:
                    # Stronger red for more negative values
                    intensity = min(1.0, abs(values[i]) / 20.0)  # Normalize up to -20
                    bar.set_color((1.0, 0.3 * (1 - intensity), 0.3 * (1 - intensity)))
                else:
                    # Light red/pink for low positive values
                    normalized_value = values[i] / 2.0  # Normalize up to 2
                    intensity = max(0, 1 - normalized_value)
                    bar.set_color((1.0, 0.7 * intensity, 0.7 * intensity))
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                        f"{width:.2f} pts/credit", ha='left', va='center', fontsize=8)
            
            # Set consistent x-axis limits
            ax2.set_xlim(data.get('underp_scale_min', -22), data.get('underp_scale_max', 3))
            
            ax2.set_title(f'Underperforming Drivers', fontsize=11)
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No underperforming driver data available",
                   ha='center', va='center', transform=ax2.transAxes)
            ax2.axis('off')
        
        # Bottom left: Team performance
        ax3 = self.figure.add_subplot(gs[1, 0])
        
        # Get team performance data
        team_performance = data.get('team_performance', [])
        
        if team_performance:
            # Sort by points (best at top)
            team_performance.sort(key=lambda x: x['points'], reverse=False)
            
            # Format for display
            team_names = [t['name'] for t in team_performance]
            team_points = [t['points'] for t in team_performance]
            
            # Create horizontal bar chart
            bars = ax3.barh(team_names, team_points)
            
            # Add team-specific colors if available
            team_colors = data.get('team_colors', {})
            for i, bar in enumerate(bars):
                team_id = team_performance[i].get('team_id')
                if team_id in team_colors:
                    bar.set_color(team_colors[team_id])
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax3.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{width:.1f}", ha='left', va='center', fontsize=9)
            
            # Set consistent x-axis limits
            ax3.set_xlim(data.get('team_scale_min', -25), data.get('team_scale_max', 70))
            
            ax3.set_title(f'Team Performance', fontsize=11)
            ax3.grid(axis='x', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, "No team performance data available",
                   ha='center', va='center', transform=ax3.transAxes)
            ax3.axis('off')
        
        # Bottom right: Driver point gaps
        ax4 = self.figure.add_subplot(gs[1, 1])
        
        # Get driver gap data
        player_driver_gaps = data.get('player_driver_gaps', {})
        
        if player_driver_gaps:
            players = player_driver_gaps.get('players', [])
            driver1_values = player_driver_gaps.get('driver1_values', [])
            driver2_values = player_driver_gaps.get('driver2_values', [])
            driver1_labels = player_driver_gaps.get('driver1_labels', [])
            driver2_labels = player_driver_gaps.get('driver2_labels', [])
            
            if players and driver1_values and driver2_values:
                # Calculate positions for grouped bars
                x = np.arange(len(players))
                width = 0.35
                
                # Plot bars for higher scoring driver
                bars1 = ax4.bar(x - width/2, driver1_values, width, label='Higher scoring driver', color='royalblue')
                
                # Plot bars for lower scoring driver
                bars2 = ax4.bar(x + width/2, driver2_values, width, label='Lower scoring driver', color='crimson')
                
                # Add zero line
                ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                
                # Add driver labels and point values
                for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                    # Add driver IDs
                    ax4.annotate(f"{driver1_labels[i]}",
                                xy=(bar1.get_x() + bar1.get_width()/2, driver1_values[i]),
                                xytext=(0, 3 if driver1_values[i] >= 0 else -3),
                                textcoords="offset points",
                                ha='center', va='bottom' if driver1_values[i] >= 0 else 'top',
                                fontsize=8, rotation=90)
                    
                    ax4.annotate(f"{driver2_labels[i]}",
                                xy=(bar2.get_x() + bar2.get_width()/2, driver2_values[i]),
                                xytext=(0, 3 if driver2_values[i] >= 0 else -3),
                                textcoords="offset points",
                                ha='center', va='bottom' if driver2_values[i] >= 0 else 'top',
                                fontsize=8, rotation=90)
                    
                    # Add point values inside bars when there's enough space
                    if abs(driver1_values[i]) > 5:
                        ax4.text(bar1.get_x() + bar1.get_width()/2, driver1_values[i]/2,
                                f"{driver1_values[i]:.1f}", ha='center', va='center',
                                fontsize=8, color='white' if abs(driver1_values[i]) > 15 else 'black')
                    
                    if abs(driver2_values[i]) > 5:
                        ax4.text(bar2.get_x() + bar2.get_width()/2, driver2_values[i]/2,
                                f"{driver2_values[i]:.1f}", ha='center', va='center',
                                fontsize=8, color='white' if abs(driver2_values[i]) > 15 else 'black')
                
                # Set axis settings
                ax4.set_xticks(x)
                ax4.set_xticklabels(players, rotation=45, ha='right')
                ax4.set_ylim(data.get('gap_scale_min', -25), data.get('gap_scale_max', 65))
                ax4.set_ylabel('Points')
                ax4.set_title('Driver Point Gaps', fontsize=11)
                ax4.legend(fontsize=8)
                ax4.grid(axis='y', alpha=0.3)
            else:
                ax4.text(0.5, 0.5, "Insufficient driver gap data",
                       ha='center', va='center', transform=ax4.transAxes)
                ax4.axis('off')
        else:
            ax4.text(0.5, 0.5, "No driver gap data available",
                   ha='center', va='center', transform=ax4.transAxes)
            ax4.axis('off')
        
        # Add overall title
        self.figure.suptitle(f'Fantasy Impact Events: {race_name}', fontsize=14, fontweight='bold')
    
    def show_player_standings_impact(self, race_id, race_name, data):
        """Show player standings impact visualization
        
        Args:
            race_id (str): Race ID
            race_name (str): Race name
            data (dict): Standings impact data
        """
        # Create a figure with 2x2 layout
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1.2], width_ratios=[1, 1])
        
        # Top left - Position changes
        ax1 = self.figure.add_subplot(gs[0, 0])
        
        # Get position changes data
        position_changes = data.get('position_changes', [])
        
        if position_changes:
            # Format for display
            player_names = [p['player_name'] for p in position_changes]
            position_deltas = [p['position_delta'] for p in position_changes]
            
            # Create horizontal bar chart
            bars = ax1.barh(player_names, position_deltas)
            
            # Color bars by value
            for i, bar in enumerate(bars):
                if position_deltas[i] > 0:
                    bar.set_color('forestgreen')
                elif position_deltas[i] < 0:
                    bar.set_color('firebrick')
                else:
                    bar.set_color('silver')
            
            # Add zero line
            ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                if width != 0:
                    ax1.text(width + 0.1 if width > 0 else width - 0.1, 
                            bar.get_y() + bar.get_height()/2,
                            f"{width:+.0f}", 
                            ha='left' if width > 0 else 'right', 
                            va='center', fontsize=9)
            
            ax1.set_title(f'Position Changes After Race', fontsize=11)
            ax1.grid(axis='x', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "No position change data available",
                   ha='center', va='center', transform=ax1.transAxes)
            ax1.axis('off')
        
        # Top right - Points gained in this race
        ax2 = self.figure.add_subplot(gs[0, 1])
        
        # Get race points data
        race_points = data.get('race_points', [])
        
        if race_points:
            # Sort by points (smallest first for better display)
            race_points.sort(key=lambda x: x['points'], reverse=False)
            
            # Format for display
            player_names = [p['player_name'] for p in race_points]
            points = [p['points'] for p in race_points]
            
            # Create horizontal bar chart
            bars = ax2.barh(player_names, points)
            
            # Color bars by value
            cmap = plt.cm.Blues
            max_value = max(points) if points else 1
            min_value = min(points) if points else 0
            value_range = max_value - min_value
            
            for i, bar in enumerate(bars):
                normalized_value = (points[i] - min_value) / (value_range + 0.1)
                bar.set_color(cmap(0.3 + 0.7 * normalized_value))
            
            # Add value annotations
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                        f"{width:.1f}", ha='left', va='center', fontsize=9)
            
            ax2.set_title(f'Points Gained in Race', fontsize=11)
            ax2.grid(axis='x', alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No race points data available",
                   ha='center', va='center', transform=ax2.transAxes)
            ax2.axis('off')
        
        # Bottom - Standings table
        ax3 = self.figure.add_subplot(gs[1, :])
        
        # Get standings table data
        standings_table = data.get('standings_table', {})
        
        if standings_table:
            column_labels = standings_table.get('column_labels', [])
            table_data = standings_table.get('table_data', [])
            
            if column_labels and table_data:
                # Create the table
                table = ax3.table(
                    cellText=table_data,
                    colLabels=column_labels,
                    loc='center',
                    cellLoc='center'
                )
                
                # Style the table
                table.auto_set_font_size(False)
                table.set_fontsize(9)
                
                # Set column widths
                col_widths = standings_table.get('col_widths', [0.1, 0.3, 0.15, 0.15, 0.1, 0.15, 0.1])
                for i, width in enumerate(col_widths):
                    for j in range(len(table_data) + 1):  # +1 for header
                        if j < len(table_data) + 1 and i < len(col_widths):
                            cell = table[j, i]
                            cell.set_width(width)
                
                # Color header
                for i in range(len(column_labels)):
                    if i < len(column_labels):
                        table[0, i].set_facecolor('#4472C4')
                        table[0, i].set_text_props(color='white', fontweight='bold')
                
                # Color rows
                for i in range(len(table_data)):
                    row_num = i + 1  # Skip header
                    
                    # Alternate row colors
                    if i % 2 == 0:
                        color = '#D9E1F2'  # Light blue
                    else:
                        color = '#E9EDF4'  # Even lighter blue
                    
                    for j in range(len(column_labels)):
                        if j < len(column_labels):
                            table[row_num, j].set_facecolor(color)
                            
                            # Highlight position changes in the last column
                            if j == 6 and isinstance(table_data[i][j], (int, float)):
                                change = table_data[i][j]
                                if change > 0:
                                    table[row_num, j].set_facecolor('#C6E0B4')  # Light green
                                elif change < 0:
                                    table[row_num, j].set_facecolor('#F8CBAD')  # Light red
                
                # Hide axes and set title
                ax3.set_title('Standings Table', fontsize=11)
            else:
                ax3.text(0.5, 0.5, "Insufficient standings table data",
                       ha='center', va='center', transform=ax3.transAxes)
            
            # Hide axes
            ax3.axis('off')
        else:
            ax3.text(0.5, 0.5, "No standings table data available",
                   ha='center', va='center', transform=ax3.transAxes)
            ax3.axis('off')
        
        # Add overall title
        self.figure.suptitle(f'Standings Impact: {race_name}', fontsize=14, fontweight='bold')
    
    def on_update(self):
        """Handle update analysis button click"""
        if self.controller:
            race_id = self.get_selected_race()
            view_type = self.get_selected_view()
            if race_id:
                self.controller.update_visualization(race_id, view_type)
            else:
                self.show_placeholder("Please select a race")