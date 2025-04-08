"""
views/visualization/head_to_head.py - Head-to-head comparison between players
"""

from views.visualization.base_visualization import BaseVisualization
import tkinter as tk
from tkinter import ttk
import numpy as np

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
        player_frame = ttk.Frame(self.controls_frame)
        player_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(player_frame, text="Player 1:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player1_var = tk.StringVar()
        self.player1_dropdown = ttk.Combobox(player_frame, textvariable=self.player1_var, state="readonly")
        self.player1_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(player_frame, text="Player 2:").pack(side=tk.LEFT, padx=5, pady=5)
        self.player2_var = tk.StringVar()
        self.player2_dropdown = ttk.Combobox(player_frame, textvariable=self.player2_var, state="readonly")
        self.player2_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(player_frame, text="Compare", command=self.on_update).pack(side=tk.LEFT, padx=5, pady=5)
    
    def get_title(self):
        """Get the title for this visualization"""
        return "Head-to-Head Comparison"
    
    def set_player_options(self, player_options):
        """Set player dropdown options
        
        Args:
            player_options (list): List of player options
        """
        self.player1_dropdown['values'] = player_options
        self.player2_dropdown['values'] = player_options
        
        # Set default selections if options available
        if player_options:
            self.player1_dropdown.current(0)
            if len(player_options) > 1:
                self.player2_dropdown.current(1)
            else:
                self.player2_dropdown.current(0)
    
    def get_selected_players(self):
        """Get selected players
        
        Returns:
            tuple: (player1_id, player2_id)
        """
        player1 = self.player1_var.get()
        player2 = self.player2_var.get()
        
        if not player1 or not player2:
            return None, None
        
        # Extract player IDs
        player1_id = player1.split('(')[-1].split(')')[0]
        player2_id = player2.split('(')[-1].split(')')[0]
        
        return player1_id, player2_id
    
    def update(self, data):
        """Update the visualization with new data
        
        Args:
            data (dict): Contains:
                - completed_races (list): List of completed race IDs
                - race_dates (dict): Mapping of race ID to date
                - player1_data (dict): First player's data
                - player2_data (dict): Second player's data
                - head_to_head_stats (dict): Head-to-head statistics
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
        
        # Create grid for subplots
        gs = self.figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[2, 1])
        
        # Race-by-race comparison (top left)
        ax1 = self.figure.add_subplot(gs[0, 0])
        
        # Get race points for each player
        player1_points = [player1_data.get('race_points', {}).get(race, 0) for race in completed_races]
        player2_points = [player2_data.get('race_points', {}).get(race, 0) for race in completed_races]
        
        x = np.arange(len(completed_races))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, player1_points, width, label=player1_data.get('name', 'Player 1'), color='royalblue')
        bars2 = ax1.bar(x + width/2, player2_points, width, label=player2_data.get('name', 'Player 2'), color='darkorange')
        
        # Add values on top of bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.annotate(f'{height:.1f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)
        
        ax1.set_title(f'Race-by-Race Comparison', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(completed_races, rotation=45)
        ax1.set_ylabel('Points', fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        ax1.legend()
        
        # Cumulative points comparison (bottom left)
        ax2 = self.figure.add_subplot(gs[1, 0])
        
        player1_cumulative = player1_data.get('cumulative_points', [])
        player2_cumulative = player2_data.get('cumulative_points', [])
        
        ax2.plot(completed_races, player1_cumulative, 'o-', linewidth=2, label=player1_data.get('name', 'Player 1'), color='royalblue')
        ax2.plot(completed_races, player2_cumulative, 'o-', linewidth=2, label=player2_data.get('name', 'Player 2'), color='darkorange')
        
        # Add final point values
        if player1_cumulative:
            ax2.annotate(f'{player1_cumulative[-1]:.1f}',
                       xy=(completed_races[-1], player1_cumulative[-1]),
                       xytext=(5, 0),
                       textcoords="offset points",
                       fontsize=9, fontweight='bold', color='royalblue')
        
        if player2_cumulative:
            ax2.annotate(f'{player2_cumulative[-1]:.1f}',
                       xy=(completed_races[-1], player2_cumulative[-1]),
                       xytext=(5, 0),
                       textcoords="offset points",
                       fontsize=9, fontweight='bold', color='darkorange')
        
        ax2.set_title(f'Cumulative Points', fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(completed_races, rotation=45)
        ax2.set_ylabel('Cumulative Points', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Head-to-head stats (right side)
        ax3 = self.figure.add_subplot(gs[:, 1])
        ax3.axis('off')
        
        # Format and display stats
        stats_text = (
            f"Total Races: {head_to_head_stats.get('total_races', 0)}\n\n"
            f"Race Wins:\n"
            f"{player1_data.get('name', 'Player 1')}: {head_to_head_stats.get('player1_wins', 0)}\n"
            f"{player2_data.get('name', 'Player 2')}: {head_to_head_stats.get('player2_wins', 0)}\n"
            f"Draws: {head_to_head_stats.get('draws', 0)}\n\n"
            f"Total Points:\n"
            f"{player1_data.get('name', 'Player 1')}: {head_to_head_stats.get('player1_total', 0):.1f}\n"
            f"{player2_data.get('name', 'Player 2')}: {head_to_head_stats.get('player2_total', 0):.1f}\n"
            f"Difference: {abs(head_to_head_stats.get('player1_total', 0) - head_to_head_stats.get('player2_total', 0)):.1f}\n\n"
            f"Average Points Per Race:\n"
            f"{player1_data.get('name', 'Player 1')}: {head_to_head_stats.get('player1_avg', 0):.2f}\n"
            f"{player2_data.get('name', 'Player 2')}: {head_to_head_stats.get('player2_avg', 0):.2f}\n\n"
            f"Best Race Performance:\n"
            f"{player1_data.get('name', 'Player 1')}: {head_to_head_stats.get('player1_best', 0):.1f} pts ({head_to_head_stats.get('player1_best_race', 'N/A')})\n"
            f"{player2_data.get('name', 'Player 2')}: {head_to_head_stats.get('player2_best', 0):.1f} pts ({head_to_head_stats.get('player2_best_race', 'N/A')})"
        )
        
        ax3.text(0.5, 0.5, stats_text, 
                horizontalalignment='center', verticalalignment='center',
                transform=ax3.transAxes, fontsize=10, linespacing=1.5)
        
        # Set title
        self.figure.suptitle(f'Head-to-Head: {player1_data.get("name", "Player 1")} vs {player2_data.get("name", "Player 2")}', 
                            fontsize=14, fontweight='bold')
        
        # Adjust layout
        self.figure.tight_layout(rect=[0, 0, 1, 0.95])  # Leave room for suptitle
        self.canvas.draw()
    
    def on_update(self):
        """Handle update button click"""
        player1_id, player2_id = self.get_selected_players()
        if not player1_id or not player2_id:
            self.show_placeholder("Please select two players to compare")
            return
            
        if player1_id == player2_id:
            self.show_placeholder("Please select two different players to compare")
            return
            
        if self.controller:
            self.controller.update_visualization(player1_id, player2_id)