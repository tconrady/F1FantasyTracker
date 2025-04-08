"""
controllers/standings_controller.py - Controller for standings view
"""

import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

class StandingsController:
    """
    Controller for standings view.
    Handles actions related to showing season standings and race breakdowns.
    """
    
    def __init__(self, view, data_manager):
        """
        Initialize the standings controller.
        
        Args:
            view: The standings view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Connect view events to controller methods
        self.connect_view_events()
        
        # Load data
        self.load_data()
    
    def connect_view_events(self):
        """Connect view event handlers to controller methods"""
        self.view.on_show_standings = self.show_standings
        self.view.on_show_race_breakdown = self.show_race_breakdown
        self.view.on_refresh_data = self.load_data
    
    def load_data(self):
        """Load data from the data manager and update the view"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Update race dropdown options
        races = data['races']
        completed_races = races[races['Status'] == 'Completed']
        race_display = [f"{row['RaceID']} - {row['Name']}" for _, row in completed_races.iterrows()]
        
        self.view.set_race_options(race_display)
    
    def show_standings(self):
        """Show season standings visualization"""
        try:
            # Load data
            data = self.data_manager.load_data()
            if not data:
                self.view.show_placeholder("No data available")
                return
            
            # Get completed races
            races = data['races']
            races = races.sort_values(by='Date')
            completed_races = races[races['Status'] == 'Completed']['RaceID'].tolist()
            
            if not completed_races:
                self.view.show_placeholder("No completed races found")
                return
            
            # Get race dates
            race_dates = {
                race_id: races[races['RaceID'] == race_id]['Date'].iloc[0].strftime('%Y-%m-%d')
                for race_id in completed_races
            }
            
            # Get all players
            players = data['player_results']['PlayerID'].unique()
            
            # Get player names
            player_picks = data['player_picks']
            player_names = {
                player_id: player_picks[player_picks['PlayerID'] == player_id]['PlayerName'].iloc[0]
                for player_id in players if not player_picks[player_picks['PlayerID'] == player_id].empty
            }
            
            # Calculate player data for visualization
            player_data = []
            
            for player_id in players:
                player_name = player_names.get(player_id, f"Player {player_id}")
                cumulative_points = []
                points_so_far = 0
                
                for race_id in completed_races:
                    # Get player's result for this race
                    player_race = data['player_results'][
                        (data['player_results']['PlayerID'] == player_id) & 
                        (data['player_results']['RaceID'] == race_id)
                    ]
                    
                    if not player_race.empty:
                        # Add per-race points to running total
                        points_so_far += player_race.iloc[0]['Points']
                    
                    cumulative_points.append(points_so_far)
                
                player_data.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'cumulative_points': cumulative_points
                })
            
            # Prepare data for visualization
            standings_data = {
                'completed_races': completed_races,
                'race_dates': race_dates,
                'player_data': player_data
            }
            
            # Update the view
            self.view.show_season_standings(standings_data)
        except Exception as e:
            logger.exception("Error showing standings")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.view.show_placeholder("Error showing standings")
    
    def show_race_breakdown(self):
        """Show race breakdown visualization"""
        try:
            # Get selected race
            race_selection = self.view.get_selected_race()
            if not race_selection:
                messagebox.showerror("Error", "Please select a race")
                return
            
            # Extract race ID
            race_id = race_selection.split('-')[0].strip()
            
            # Load data
            data = self.data_manager.load_data()
            if not data:
                self.view.show_placeholder("No data available")
                return
            
            # Get race details
            race_info = data['races'][data['races']['RaceID'] == race_id]
            if race_info.empty:
                self.view.show_placeholder(f"Race {race_id} not found")
                return
                
            race_name = race_info.iloc[0]['Name']
            
            # Get player results for this race
            player_results = data['player_results'][data['player_results']['RaceID'] == race_id]
            if player_results.empty:
                self.view.show_placeholder(f"No results found for race {race_id}")
                return
            
            # Get player names
            player_picks = data['player_picks']
            
            # Process player results
            processed_results = []
            
            for _, result in player_results.iterrows():
                player_id = result['PlayerID']
                player_picks_row = player_picks[player_picks['PlayerID'] == player_id]
                player_name = player_picks_row['PlayerName'].iloc[0] if not player_picks_row.empty else f"Player {player_id}"
                
                processed_results.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'points': result['Points'],
                    'calculation_details': result['CalculationDetails'] if 'CalculationDetails' in result else ""
                })
            
            # Prepare data for visualization
            breakdown_data = {
                'race_id': race_id,
                'race_name': race_name,
                'player_results': processed_results
            }
            
            # Update the view
            self.view.show_race_breakdown(breakdown_data)
            
            # Show detailed breakdown in a dialog
            self.show_detailed_breakdown(breakdown_data)
        except Exception as e:
            logger.exception("Error showing race breakdown")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.view.show_placeholder("Error showing race breakdown")
    
    def show_detailed_breakdown(self, breakdown_data):
        """Show detailed breakdown in a dialog
        
        Args:
            breakdown_data (dict): Breakdown data dictionary
        """
        race_id = breakdown_data['race_id']
        race_name = breakdown_data['race_name']
        player_results = breakdown_data['player_results']
        
        # Create dialog
        dialog = tk.Toplevel()
        dialog.title(f"Detailed Breakdown for {race_id}")
        dialog.geometry("600x400")
        dialog.transient()
        
        # Create text widget
        text = tk.Text(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add breakdown details
        text.insert(tk.END, f"DETAILED BREAKDOWN FOR {race_name} ({race_id})\n")
        text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Sort by points (descending)
        player_results.sort(key=lambda x: x['points'], reverse=True)
        
        for result in player_results:
            player_name = result['player_name']
            points = result['points']
            
            text.insert(tk.END, f"{player_name}: {points} points\n")
            
            if result['calculation_details']:
                text.insert(tk.END, f"  Calculation: {result['calculation_details']}\n")
            
            text.insert(tk.END, "-" * 50 + "\n")
        
        # Make read-only
        text.configure(state='disabled')
        
        # Add a close button
        tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)