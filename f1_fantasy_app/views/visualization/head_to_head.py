"""
views/visualization/head_to_head.py - Head-to-head comparison visualization
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

class HeadToHeadVisualization(BaseVisualization):
    """Head-to-head comparison visualization between two players"""
    
    def __init__(self, parent, controller):
        """
        Initialize the head-to-head visualization.
        
        Args:
            parent: The parent widget
            controller: The controller for this visualization
        """
        super().__init__(parent, controller)
        
        # Set up controls
        controls_frame = ttk.Frame(self.controls_frame)
        controls_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Player 1:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player1_var = tk.StringVar()
        self.player1_dropdown = ttk.Combobox(controls_frame, textvariable=self.player1_var, state="readonly")
        self.player1_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Player 2:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player2_var = tk.StringVar()
        self.player2_dropdown = ttk.Combobox(controls_frame, textvariable=self.player2_var, state="readonly")
        self.player2_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Compare", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Head-to-Head Comparison"
    
    def set_player_options(self, player_options):
        """Set player dropdown options
        
        Args:
            player_options (list): List of player option strings
        """
        self.player1_dropdown['values'] = player_options
        self.player2_dropdown['values'] = player_options
        
        # Select first two different players by default if available
        if len(player_options) > 1:
            self.player1_dropdown.current(0)
            self.player2_dropdown.current(1)
        elif player_options:
            self.player1_dropdown.current(0)
    
    def get_selected_players(self):
        """Get selected players
        
        Returns:
            tuple: (player1_id, player2_id) or (None, None) if not selected
        """
        player1 = self.player1_var.get()
        player2 = self.player2_var.get()
        
        if not player1 or not player2:
            return None, None
        
        # Extract player IDs
        if '(' in player1 and ')' in player1:
            player1_id = player1.split('(')[-1].split(')')[0]
        else:
            player1_id = player1
            
        if '(' in player2 and ')' in player2:
            player2_id = player2.split('(')[-1].split(')')[0]
        else:
            player2_id = player2
            
        return player1_id, player2_id
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Dictionary mapping race ID to date string
                - player1_data (dict): Dictionary with player1 data
                - player2_data (dict): Dictionary with player2 data
                - head_to_head_stats (dict): Dictionary with head-to-head statistics
        """
        if not data:
            self.show_placeholder("No data available for visualization")
            return
        
        completed_races = data.get('completed_races', [])
        race_dates = data.get('race_dates', {})
        player1_data = data.get('player1_data', {})
        player2_data = data.get('player2_data', {})
        head_to_head_stats = data.get('head_to_head_stats', {})
        
        if not completed_races or not player1_data or not player2_data:
            self.show_placeholder("Insufficient data for comparison")
            return
        
        # Clear previous plot
        self.figure.clear()
        
        # Create three subplots in a 2x2 grid with specific height and width ratios
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[2, 1])
        
        ax1 = self.figure.add_subplot(gs[0, 0])  # Race-by-race comparison
        ax2 = self.figure.add_subplot(gs[1, 0])  # Cumulative points
        ax3 = self.figure.add_subplot(gs[:, 1])  # Head-to-head stats
        
        # Race-by-race comparison
        player1_name = player1_data.get('name', 'Player 1')
        player2_name = player2_data.get('name', 'Player 2')
        
        player1_race_points = player1_data.get('race_points', {})
        player2_race_points = player2_data.get('race_points', {})
        
        x = np.arange(len(completed_races))
        width = 0.35
        
        p1_points = [player1_race_points.get(race, 0) for race in completed_races]
        p2_points = [player2_race_points.get(race, 0) for race in completed_races]
        
        bars1 = ax1.bar(x - width/2, p1_points, width, label=player1_name, color='royalblue')
        bars2 = ax1.bar(x + width/2, p2_points, width, label=player2_name, color='darkorange')
        
        # Add values on top of bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{height:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)
        
        ax1.set_title(f'Race-by-Race Comparison', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(completed_races, rotation=45)
        ax1.set_ylabel('Points', fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        ax1.legend()
        
        # Cumulative points comparison
        player1_cum = player1_data.get('cumulative_points', [])
        player2_cum = player2_data.get('cumulative_points', [])
        
        ax2.plot(completed_races, player1_cum, 'o-', linewidth=2, label=player1_name, color='royalblue')
        ax2.plot(completed_races, player2_cum, 'o-', linewidth=2, label=player2_name, color='darkorange')
        
        # Add final point values
        if player1_cum:
            ax2.annotate(f'{player1_cum[-1]:.1f}',
                       xy=(completed_races[-1], player1_cum[-1]),
                       xytext=(5, 0),
                       textcoords="offset points",
                       fontsize=9, fontweight='bold', color='royalblue')
        
        if player2_cum:
            ax2.annotate(f'{player2_cum[-1]:.1f}',
                       xy=(completed_races[-1], player2_cum[-1]),
                       xytext=(5, 0),
                       textcoords="offset points",
                       fontsize=9, fontweight='bold', color='darkorange')
        
        ax2.set_title(f'Cumulative Points', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(completed_races, rotation=45)
        ax2.set_ylabel('Cumulative Points', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Head-to-head stats as text
        ax3.axis('off')
        
        # Format stats
        total_races = head_to_head_stats.get('total_races', 0)
        p1_wins = head_to_head_stats.get('player1_wins', 0)
        p2_wins = head_to_head_stats.get('player2_wins', 0)
        draws = head_to_head_stats.get('draws', 0)
        
        p1_total = head_to_head_stats.get('player1_total', 0)
        p2_total = head_to_head_stats.get('player2_total', 0)
        diff = abs(p1_total - p2_total)
        
        p1_avg = head_to_head_stats.get('player1_avg', 0)
        p2_avg = head_to_head_stats.get('player2_avg', 0)
        
        p1_best = head_to_head_stats.get('player1_best', 0)
        p2_best = head_to_head_stats.get('player2_best', 0)
        
        p1_best_race = head_to_head_stats.get('player1_best_race', 'None')
        p2_best_race = head_to_head_stats.get('player2_best_race', 'None')
        
        # Draw stats table as text
        ax3.set_title(f'Head-to-Head Stats', fontsize=12)
        
        stats_text = (
            f"Total Races: {total_races}\n\n"
            f"Race Wins:\n"
            f"{player1_name}: {p1_wins}\n"
            f"{player2_name}: {p2_wins}\n"
            f"Draws: {draws}\n\n"
            f"Total Points:\n"
            f"{player1_name}: {p1_total:.1f}\n"
            f"{player2_name}: {p2_total:.1f}\n"
            f"Difference: {diff:.1f}\n\n"
            f"Average Points Per Race:\n"
            f"{player1_name}: {p1_avg:.2f}\n"
            f"{player2_name}: {p2_avg:.2f}\n\n"
            f"Best Race Performance:\n"
            f"{player1_name}: {p1_best:.1f} pts ({p1_best_race})\n"
            f"{player2_name}: {p2_best:.1f} pts ({p2_best_race})"
        )
        
        ax3.text(0.5, 0.5, stats_text, 
                horizontalalignment='center', verticalalignment='center',
                transform=ax3.transAxes, fontsize=10, linespacing=1.5)
        
        # Improve layout
        self.figure.tight_layout()
        self.canvas.draw()
    
    def on_update(self):
        """Handle compare button click"""
        if self.controller:
            player1_id, player2_id = self.get_selected_players()
            if player1_id and player2_id:
                self.controller.update_visualization(player1_id, player2_id)
            else:
                self.show_placeholder("Please select two players to compare")