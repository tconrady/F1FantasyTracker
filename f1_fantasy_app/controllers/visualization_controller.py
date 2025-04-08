"""
controllers/visualization_controller.py - Controllers for visualizations
"""

import logging
import pandas as pd
import numpy as np
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeasonProgressController:
    """Controller for Season Progress visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
    
    def initialize(self):
        """Initialize the visualization"""
        # Show placeholder
        self.view.show_placeholder("Click 'Update Visualization' to show season progress")
    
    def update_visualization(self):
        """Update the visualization with current data"""
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
        
        # Calculate per-race points for each player
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
        viz_data = {
            'completed_races': completed_races,
            'race_dates': race_dates,
            'player_data': player_data
        }
        
        # Update the view
        self.view.update(viz_data)

class PointsTableController:
    """Controller for Points Table visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Set driver options
        driver_options = ["All Drivers"]
        for _, driver in data['drivers'].sort_values(by='Name').iterrows():
            driver_name = driver['Name']
            driver_id = driver['DriverID']
            driver_options.append(f"{driver_name} ({driver_id})")
        
        self.view.set_driver_options(driver_options)
        
        # Set player options
        player_options = ["All Players"]
        for player_id in data['player_results']['PlayerID'].unique():
            player_picks = data['player_picks'][data['player_picks']['PlayerID'] == player_id]
            if not player_picks.empty:
                player_name = player_picks['PlayerName'].iloc[0]
                player_options.append(f"{player_name} ({player_id})")
        
        self.view.set_player_options(player_options)
        
        # Show placeholder
        self.view.show_placeholder("Select a driver or player and click 'Update Table'")
    
    def update_table(self, table_type):
        """
        Update the points table.
        
        Args:
            table_type (str): 'driver' or 'player'
        """
        # Get selected driver or player
        if table_type == 'driver':
            selection = self.view.get_selected_driver()
            selected_id = None
            
            if selection != "All Drivers":
                # Extract ID
                selected_id = selection.split('(')[1].split(')')[0]
        else:  # player
            selection = self.view.get_selected_player()
            selected_id = None
            
            if selection != "All Players":
                # Extract ID
                selected_id = selection.split('(')[1].split(')')[0]
        
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
        
        # Prepare table data based on type
        if table_type == 'driver':
            table_data = self.prepare_driver_table_data(data, completed_races, selected_id)
            entity_type = "Driver"
        else:  # player
            table_data = self.prepare_player_table_data(data, completed_races, selected_id)
            entity_type = "Player"
        
        # Create column labels
        column_labels = [entity_type] + completed_races
        
        # Prepare data for visualization
        viz_data = {
            'table_type': table_type,
            'column_labels': column_labels,
            'table_data': table_data,
            'entity_type': entity_type
        }
        
        # Update the view
        self.view.update(viz_data)
    
    def prepare_driver_table_data(self, data, completed_races, selected_driver_id=None):
        """
        Prepare data for the driver points table.
        
        Args:
            data (dict): Dictionary containing all loaded dataframes
            completed_races (list): List of completed race IDs
            selected_driver_id (str, optional): ID of selected driver or None for all
            
        Returns:
            list: Table data as list of lists
        """
        table_data = []
        
        # Get drivers to display
        if selected_driver_id:
            drivers_to_show = data['drivers'][data['drivers']['DriverID'] == selected_driver_id]
        else:
            # If showing all, limit to those with data and top performers
            driver_total_points = {}
            
            for driver_id in data['drivers']['DriverID'].unique():
                driver_results = data['race_results'][data['race_results']['DriverID'] == driver_id]
                if not driver_results.empty:
                    total_points = abs(driver_results['Points'].sum())
                    driver_total_points[driver_id] = total_points
            
            # Sort by total points and take top 15
            top_drivers = sorted(driver_total_points.items(), key=lambda x: x[1], reverse=True)[:15]
            driver_ids = [d[0] for d in top_drivers]
            
            drivers_to_show = data['drivers'][data['drivers']['DriverID'].isin(driver_ids)]
        
        # Process each driver
        for _, driver in drivers_to_show.iterrows():
            driver_id = driver['DriverID']
            driver_name = driver['Name']
            
            row_data = [f"{driver_name} ({driver_id})"]  # First column
            
            for race_id in completed_races:
                # Get per-race points
                race_result = data['race_results'][
                    (data['race_results']['RaceID'] == race_id) & 
                    (data['race_results']['DriverID'] == driver_id)
                ]
                
                if not race_result.empty:
                    per_race_points = race_result.iloc[0]['Points']
                    
                    # Format cell based on what data we have
                    if 'CumulativePoints' in race_result.columns:
                        # Show both per-race and cumulative
                        cumulative = race_result.iloc[0]['CumulativePoints']
                        cell_text = f"{per_race_points:.1f} ({cumulative:.1f})"
                    else:
                        # Just per-race
                        cell_text = f"{per_race_points:.1f}"
                else:
                    cell_text = "--"
                
                row_data.append(cell_text)
            
            # Only add if we have some data
            if len([x for x in row_data[1:] if x != "--"]) > 0:
                table_data.append(row_data)
        
        return table_data
    
    def prepare_player_table_data(self, data, completed_races, selected_player_id=None):
        """
        Prepare data for the player points table.
        
        Args:
            data (dict): Dictionary containing all loaded dataframes
            completed_races (list): List of completed race IDs
            selected_player_id (str, optional): ID of selected player or None for all
            
        Returns:
            list: Table data as list of lists
        """
        table_data = []
        
        # Get player names
        player_names = {}
        for player_id in data['player_results']['PlayerID'].unique():
            player_picks = data['player_picks'][data['player_picks']['PlayerID'] == player_id]
            if not player_picks.empty:
                player_names[player_id] = player_picks['PlayerName'].iloc[0]
            else:
                player_names[player_id] = f"Player {player_id}"
        
        # Get players to display
        if selected_player_id:
            player_ids = [selected_player_id]
        else:
            # Show all players
            player_ids = list(player_names.keys())
        
        # Process each player
        for player_id in player_ids:
            player_name = player_names.get(player_id, f"Player {player_id}")
            
            row_data = [f"{player_name} ({player_id})"]  # First column
            
            for race_id in completed_races:
                # Get per-race points
                player_result = data['player_results'][
                    (data['player_results']['RaceID'] == race_id) & 
                    (data['player_results']['PlayerID'] == player_id)
                ]
                
                if not player_result.empty:
                    per_race_points = player_result.iloc[0]['Points']
                    
                    # Format cell based on what data we have
                    if 'CumulativePoints' in player_result.columns:
                        # Show both per-race and cumulative
                        cumulative = player_result.iloc[0]['CumulativePoints']
                        cell_text = f"{per_race_points:.1f} ({cumulative:.1f})"
                    else:
                        # Just per-race
                        cell_text = f"{per_race_points:.1f}"
                else:
                    cell_text = "--"
                
                row_data.append(cell_text)
            
            # Only add if we have some data
            if len([x for x in row_data[1:] if x != "--"]) > 0:
                table_data.append(row_data)
        
        return table_data

class DriverPerformanceController:
    """Controller for Driver Performance visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            return
        
        # Set driver options
        all_drivers = data['drivers'].copy()
        driver_options = [f"{row['Name']} ({row['DriverID']})" 
                         for _, row in all_drivers.sort_values(by='Name').iterrows()]
        
        self.view.set_driver_options(driver_options)
        
        # Pre-select the top 5 drivers by credits
        top_drivers = all_drivers.sort_values(by='Credits', ascending=False).head(5)['DriverID'].tolist()
        for i, option in enumerate(driver_options):
            driver_id = option.split('(')[1].split(')')[0]
            if driver_id in top_drivers:
                self.view.driver_listbox.selection_set(i)
        
        # Show placeholder
        self.view.show_placeholder("Select drivers and click 'Update Chart' to show performance")
    
    def update_visualization(self, selected_driver_ids):
        """Update the visualization with selected drivers
        
        Args:
            selected_driver_ids (list): List of selected driver IDs
        """
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
        
        # Get driver data
        driver_data = []
        
        for driver_id in selected_driver_ids:
            driver = data['drivers'][data['drivers']['DriverID'] == driver_id]
            if driver.empty:
                continue
                
            driver_name = driver.iloc[0]['Name']
            
            # Get driver's points for each race
            race_points = []
            for race_id in completed_races:
                race_result = data['race_results'][
                    (data['race_results']['RaceID'] == race_id) & 
                    (data['race_results']['DriverID'] == driver_id)
                ]
                
                if not race_result.empty:
                    race_points.append(race_result.iloc[0]['Points'])
                else:
                    # Check if there was a substitution
                    substitution = data['driver_assignments'][
                        (data['driver_assignments']['RaceID'] == race_id) & 
                        (data['driver_assignments']['SubstitutedForDriverID'] == driver_id)
                    ]
                    
                    if not substitution.empty:
                        substitute_id = substitution.iloc[0]['DriverID']
                        substitute_result = data['race_results'][
                            (data['race_results']['RaceID'] == race_id) & 
                            (data['race_results']['DriverID'] == substitute_id)
                        ]
                        
                        if not substitute_result.empty:
                            race_points.append(substitute_result.iloc[0]['Points'])
                        else:
                            race_points.append(0)
                    else:
                        race_points.append(0)
            
            # Calculate average points
            avg_points = sum(race_points) / len(race_points) if race_points else 0
            
            driver_data.append({
                'driver_id': driver_id,
                'driver_name': driver_name,
                'race_points': race_points,
                'avg_points': avg_points
            })
        
        # Prepare data for visualization
        viz_data = {
            'completed_races': completed_races,
            'race_dates': race_dates,
            'driver_data': driver_data
        }
        
        # Update the view
        self.view.update(viz_data)


class HeadToHeadController:
    """Controller for Head-to-Head visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get player options for dropdown
        player_picks = data.get('player_picks', None)
        if player_picks is None:
            self.view.show_placeholder("No player data available")
            return
            
        player_options = []
        for player_id in player_picks['PlayerID'].unique():
            player_rows = player_picks[player_picks['PlayerID'] == player_id]
            if not player_rows.empty:
                player_name = player_rows['PlayerName'].iloc[0]
                player_options.append(f"{player_name} ({player_id})")
        
        # Update view with player options
        self.view.set_player_options(player_options)
        
        # Show placeholder
        self.view.show_placeholder("Select two players and click 'Compare'")
    
    def update_visualization(self, player1_id, player2_id):
        """Update the visualization with new data
        
        Args:
            player1_id (str): ID of first player
            player2_id (str): ID of second player
        """
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get completed races
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
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
        
        # Get player results
        player_results = data.get('player_results', None)
        if player_results is None:
            self.view.show_placeholder("No player results available")
            return
            
        # Get player names
        player_picks = data.get('player_picks', None)
        player1_name = player1_id
        player2_name = player2_id
        
        if player_picks is not None:
            player1_rows = player_picks[player_picks['PlayerID'] == player1_id]
            if not player1_rows.empty:
                player1_name = player1_rows['PlayerName'].iloc[0]
                
            player2_rows = player_picks[player_picks['PlayerID'] == player2_id]
            if not player2_rows.empty:
                player2_name = player2_rows['PlayerName'].iloc[0]
        
        # Prepare player data
        player1_data = {'name': player1_name, 'race_points': {}, 'cumulative_points': []}
        player2_data = {'name': player2_name, 'race_points': {}, 'cumulative_points': []}
        
        # Calculate head-to-head stats
        head_to_head_stats = {
            'total_races': len(completed_races),
            'player1_wins': 0,
            'player2_wins': 0,
            'draws': 0,
            'player1_total': 0,
            'player2_total': 0,
            'player1_best': 0,
            'player2_best': 0,
            'player1_best_race': 'N/A',
            'player2_best_race': 'N/A'
        }
        
        # Calculate race points and stats for each player
        p1_cumul = 0
        p2_cumul = 0
        
        for race_id in completed_races:
            # Player 1
            p1_race = player_results[(player_results['PlayerID'] == player1_id) & 
                                     (player_results['RaceID'] == race_id)]
            
            if not p1_race.empty:
                p1_points = p1_race.iloc[0]['Points']
                player1_data['race_points'][race_id] = p1_points
                p1_cumul += p1_points
                head_to_head_stats['player1_total'] += p1_points
                
                # Check if best race
                if p1_points > head_to_head_stats['player1_best']:
                    head_to_head_stats['player1_best'] = p1_points
                    head_to_head_stats['player1_best_race'] = race_id
            else:
                player1_data['race_points'][race_id] = 0
                
            player1_data['cumulative_points'].append(p1_cumul)
            
            # Player 2
            p2_race = player_results[(player_results['PlayerID'] == player2_id) & 
                                     (player_results['RaceID'] == race_id)]
            
            if not p2_race.empty:
                p2_points = p2_race.iloc[0]['Points']
                player2_data['race_points'][race_id] = p2_points
                p2_cumul += p2_points
                head_to_head_stats['player2_total'] += p2_points
                
                # Check if best race
                if p2_points > head_to_head_stats['player2_best']:
                    head_to_head_stats['player2_best'] = p2_points
                    head_to_head_stats['player2_best_race'] = race_id
            else:
                player2_data['race_points'][race_id] = 0
                
            player2_data['cumulative_points'].append(p2_cumul)
            
            # Determine race winner
            p1_race_points = player1_data['race_points'].get(race_id, 0)
            p2_race_points = player2_data['race_points'].get(race_id, 0)
            
            if p1_race_points > p2_race_points:
                head_to_head_stats['player1_wins'] += 1
            elif p2_race_points > p1_race_points:
                head_to_head_stats['player2_wins'] += 1
            else:
                head_to_head_stats['draws'] += 1
        
        # Calculate averages
        if completed_races:
            head_to_head_stats['player1_avg'] = head_to_head_stats['player1_total'] / len(completed_races)
            head_to_head_stats['player2_avg'] = head_to_head_stats['player2_total'] / len(completed_races)
        
        # Prepare data for view
        viz_data = {
            'completed_races': completed_races,
            'race_dates': race_dates,
            'player1_data': player1_data,
            'player2_data': player2_data,
            'head_to_head_stats': head_to_head_stats
        }
        
        # Update view
        self.view.update(viz_data)

class CreditEfficiencyController:
    """Controller for Credit Efficiency visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get race options for dropdown
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        # Get completed races
        races = races.sort_values(by='Date')
        completed_races = races[races['Status'] == 'Completed']
        
        race_options = []
        for _, race in completed_races.iterrows():
            race_id = race['RaceID']
            race_name = race['Name']
            race_options.append(f"{race_id} - {race_name}")
        
        # Update view with race options
        self.view.set_race_options(race_options)
        
        # Show placeholder
        self.view.show_placeholder("Select a race and click 'Update Chart'")
    
    def update_visualization(self, race_id):
        """Update the visualization with new data
        
        Args:
            race_id (str): Selected race ID or "All Races"
        """
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get drivers data
        drivers = data.get('drivers', None)
        if drivers is None:
            self.view.show_placeholder("No driver data available")
            return
            
        # Get race results
        race_results = data.get('race_results', None)
        if race_results is None:
            self.view.show_placeholder("No race results available")
            return
            
        # Get completed races
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        completed_races = races[races['Status'] == 'Completed']['RaceID'].tolist()
        
        # Determine if we're using theoretical data
        is_theoretical = (not completed_races or (race_id != "All Races" and 
                        race_id not in race_results['RaceID'].unique()))
        
        note = ""
        if is_theoretical:
            note = "Using theoretical data based on driver credits (no race results yet)."
        elif race_id != "All Races":
            note = f"Showing actual efficiency for {race_id}."
        else:
            note = f"Showing average efficiency across {len(completed_races)} races."
            
        # Calculate driver efficiency data
        driver_data = []
        
        for _, driver in drivers.iterrows():
            driver_id = driver['DriverID']
            driver_name = driver['Name']
            driver_credits = driver['Credits']
            
            if driver_credits <= 0:  # Skip reserve drivers
                continue
                
            # Calculate average points
            if race_id == "All Races":
                # Average across all completed races
                driver_results = race_results[race_results['DriverID'] == driver_id]
                if not driver_results.empty:
                    avg_points = driver_results['Points'].mean()
                else:
                    avg_points = 0.0
            else:
                # Only for specific race
                driver_race = race_results[(race_results['DriverID'] == driver_id) & 
                                         (race_results['RaceID'] == race_id)]
                if not driver_race.empty:
                    avg_points = driver_race.iloc[0]['Points']
                else:
                    # No results, use theoretical
                    avg_points = driver_credits * 5.0  # Simple model: credits × 5
                    is_theoretical = True
            
            # Calculate efficiency
            efficiency = 0.0
            if driver_credits > 0:
                efficiency = avg_points / driver_credits
            
            driver_data.append({
                'driver_id': driver_id,
                'name': f"{driver_name} ({driver_id})",
                'credits': driver_credits,
                'avg_points': avg_points,
                'efficiency': efficiency
            })
        
        # Prepare data for view
        viz_data = {
            'race_id': race_id,
            'is_theoretical': is_theoretical,
            'note': note,
            'driver_data': driver_data,
            'total_races': len(completed_races) if race_id == "All Races" else 1
        }
        
        # Update view
        self.view.update(viz_data)

class PointsBreakdownController:
    """Controller for Points Breakdown visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get player options for dropdown
        player_picks = data.get('player_picks', None)
        if player_picks is None:
            self.view.show_placeholder("No player data available")
            return
            
        player_options = []
        for player_id in player_picks['PlayerID'].unique():
            player_rows = player_picks[player_picks['PlayerID'] == player_id]
            if not player_rows.empty:
                player_name = player_rows['PlayerName'].iloc[0]
                player_options.append(f"{player_name} ({player_id})")
        
        # Update view with player options
        self.view.set_player_options(player_options)
        
        # Show placeholder
        self.view.show_placeholder("Select a player and click 'Update Chart'")
    
    def update_visualization(self, player_id):
        """Update the visualization with new data
        
        Args:
            player_id (str): Selected player ID
        """
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get player name
        player_picks = data.get('player_picks', None)
        if player_picks is None:
            self.view.show_placeholder("No player data available")
            return
            
        player_name = player_id
        player_rows = player_picks[player_picks['PlayerID'] == player_id]
        if not player_rows.empty:
            player_name = player_rows['PlayerName'].iloc[0]
        
        # Get completed races
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        completed_races = races[races['Status'] == 'Completed']['RaceID'].tolist()
        
        if not completed_races:
            self.view.show_placeholder("No completed races found")
            return
        
        # Get player results
        player_results = data.get('player_results', None)
        if player_results is None:
            self.view.show_placeholder("No player results available")
            return
            
        player_race_results = player_results[player_results['PlayerID'] == player_id]
        
        # Process calculation details to extract driver points
        driver_points = {}
        race_points = {}
        
        for _, result in player_race_results.iterrows():
            race_id = result['RaceID']
            race_points[race_id] = {}
            
            if 'CalculationDetails' in result and not pd.isna(result['CalculationDetails']):
                details = result['CalculationDetails']
                parts = details.split(',')
                
                for part in parts:
                    part = part.strip()
                    if ':' in part:
                        driver_id, points_str = part.split(':', 1)
                        driver_id = driver_id.strip()
                        
                        # Handle complex formats
                        points_str = points_str.strip()
                        try:
                            points = float(points_str)
                        except ValueError:
                            # Extract the first number we find
                            import re
                            matches = re.findall(r'-?\d+(?:\.\d+)?', points_str)
                            if matches:
                                points = float(matches[0])
                            else:
                                points = 0
                        
                        # Add to dictionaries
                        if driver_id in driver_points:
                            driver_points[driver_id] += points
                        else:
                            driver_points[driver_id] = points
                        
                        race_points[race_id][driver_id] = points
        
        # Get driver names
        drivers = data.get('drivers', None)
        driver_names = {}
        
        if drivers is not None:
            for driver_id in driver_points.keys():
                driver_rows = drivers[drivers['DriverID'] == driver_id]
                if not driver_rows.empty:
                    driver_names[driver_id] = f"{driver_rows.iloc[0]['Name']} ({driver_id})"
                else:
                    driver_names[driver_id] = driver_id
        
        # Check if we have any negative values
        has_negative = any(points < 0 for points in driver_points.values())
        
        # Prepare data for view
        viz_data = {
            'player_name': player_name,
            'has_negative': has_negative,
            'driver_points': driver_points,
            'driver_names': driver_names,
            'completed_races': completed_races,
            'race_points': race_points
        }
        
        # Update view
        self.view.update(viz_data)

class RacePointsHistoryController:
    """Controller for Race Points History visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Show placeholder
        self.view.show_placeholder("Click 'Update Visualization' to show race points history")
    
    def update_visualization(self):
        """Update the visualization with current data"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
        
        # Get completed races
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
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
        
        # Get race results
        race_results = data.get('race_results', None)
        if race_results is None:
            self.view.show_placeholder("No race results available")
            return
            
        # Filter for completed races
        race_results_filtered = race_results[race_results['RaceID'].isin(completed_races)]
        
        if race_results_filtered.empty:
            self.view.show_placeholder("No race results found for completed races")
            return
        
        # Prepare data for boxplot
        box_data = []
        for race_id in completed_races:
            race_data = race_results_filtered[race_results_filtered['RaceID'] == race_id]['Points'].tolist()
            box_data.append(race_data)
        
        # Prepare data for violin plot
        violin_data = []
        for race_id in completed_races:
            race_points = race_results_filtered[race_results_filtered['RaceID'] == race_id]['Points'].tolist()
            for points in race_points:
                violin_data.append({'Race': race_id, 'Points': points})
        
        violin_df = pd.DataFrame(violin_data)
        
        # Calculate statistics
        statistics = {}
        for race_id in completed_races:
            race_data = race_results_filtered[race_results_filtered['RaceID'] == race_id]['Points']
            if not race_data.empty:
                statistics[race_id] = {
                    'mean': race_data.mean(),
                    'median': race_data.median()
                }
        
        # Prepare data for visualization
        viz_data = {
            'completed_races': completed_races,
            'race_dates': race_dates,
            'race_results': race_results_filtered.to_dict('records'),
            'box_data': box_data,
            'violin_data': violin_df,
            'statistics': statistics
        }
        
        # Update the view
        self.view.update(viz_data)

class TeamPerformanceController:
    """Controller for Team Performance visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get team options for listbox
        teams = data.get('teams', None)
        if teams is None:
            self.view.show_placeholder("No team data available")
            return
            
        team_options = [f"{row['Name']} ({row['TeamID']})" 
                       for _, row in teams.sort_values(by='Name').iterrows()]
        
        # Update view with team options
        self.view.set_team_options(team_options)
        
        # Show placeholder
        self.view.show_placeholder("Select teams and click 'Update Chart'")
    
    def update_visualization(self, selected_team_ids):
        """Update the visualization with selected teams
        
        Args:
            selected_team_ids (list): List of selected team IDs
        """
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get teams data
        teams = data.get('teams', None)
        if teams is None:
            self.view.show_placeholder("No team data available")
            return
            
        # Get driver-team mappings
        drivers = data.get('drivers', None)
        if drivers is None:
            self.view.show_placeholder("No driver data available")
            return
            
        driver_teams = {row['DriverID']: row['DefaultTeam'] for _, row in drivers.iterrows()}
        
        # Get completed races
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
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
        
        # Get race results and driver substitutions
        race_results = data.get('race_results', None)
        if race_results is None:
            self.view.show_placeholder("No race results available")
            return
            
        substitutions = data.get('driver_assignments', None)
        
        # Process team data
        team_data = []
        team_colors = {
            'RBR': '#00007D',  # Dark blue
            'FER': '#DC0000',  # Red
            'MER': '#00D2BE',  # Teal
            'MCL': '#FF8700',  # Orange
            'AST': '#006F62',  # Green
            'ALP': '#0090FF',  # Blue
            'HAS': '#787878',  # Gray
            'RBT': '#1E41FF',  # Royal blue
            'WIL': '#0082FA',  # Light blue
            'SAU': '#900000'   # Burgundy
        }
        
        for team_id in selected_team_ids:
            team_row = teams[teams['TeamID'] == team_id]
            if team_row.empty:
                continue
                
            team_name = team_row.iloc[0]['Name']
            
            # Initialize race points dictionary
            race_points = {race_id: 0 for race_id in completed_races}
            
            # Process race results for this team
            for race_id in completed_races:
                race_result = race_results[race_results['RaceID'] == race_id]
                
                # Get all drivers for this team (including substitutes)
                team_drivers = [driver_id for driver_id, team in driver_teams.items() if team == team_id]
                
                # Add substitutions for this race
                if substitutions is not None:
                    race_subs = substitutions[(substitutions['RaceID'] == race_id) & 
                                            (substitutions['TeamID'] == team_id)]
                    for _, sub in race_subs.iterrows():
                        # Add substitute driver
                        team_drivers.append(sub['DriverID'])
                        # Remove substituted driver
                        if sub['SubstitutedForDriverID'] in team_drivers:
                            team_drivers.remove(sub['SubstitutedForDriverID'])
                
                # Sum points for all team drivers
                for driver_id in team_drivers:
                    driver_result = race_result[race_result['DriverID'] == driver_id]
                    if not driver_result.empty:
                        race_points[race_id] += driver_result.iloc[0]['Points']
            
            # Calculate total points
            total_points = sum(race_points.values())
            
            team_data.append({
                'team_id': team_id,
                'team_name': team_name,
                'race_points': race_points,
                'total_points': total_points
            })
        
        # Prepare data for visualization
        viz_data = {
            'completed_races': completed_races,
            'race_dates': race_dates,
            'team_data': team_data,
            'team_colors': team_colors
        }
        
        # Update the view
        self.view.update(viz_data)

class RaceAnalysisController:
    """Controller for Race Analysis visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get race options for dropdown
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        # Get completed races
        completed_races = races[races['Status'] == 'Completed']
        
        race_options = []
        for _, race in completed_races.iterrows():
            race_id = race['RaceID']
            race_name = race['Name']
            race_options.append(f"{race_id} - {race_name}")
        
        # Update view with race options
        self.view.set_race_options(race_options)
        
        # Show placeholder
        self.view.show_placeholder("Select a race and analysis view, then click 'Update Analysis'")
    
    def update_visualization(self, race_id, view_type):
        """Update the visualization with new data
        
        Args:
            race_id (str): Selected race ID
            view_type (str): Analysis view type
        """
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get race info
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        race_info = races[races['RaceID'] == race_id]
        if race_info.empty:
            self.view.show_placeholder(f"Race {race_id} not found")
            return
            
        race_name = race_info.iloc[0]['Name']
        
        # Process data based on view type
        if view_type == "Performance Summary":
            view_data = self.prepare_performance_summary(data, race_id)
        elif view_type == "Fantasy Impact Events":
            view_data = self.prepare_fantasy_impact_events(data, race_id)
        elif view_type == "Player Standings Impact":
            view_data = self.prepare_player_standings_impact(data, race_id)
        else:
            view_data = {}
        
        # Prepare data for visualization
        viz_data = {
            'race_id': race_id,
            'race_name': race_name,
            'view_type': view_type,
            'view_data': view_data
        }
        
        # Update the view
        self.view.update(viz_data)
    
    def prepare_performance_summary(self, data, race_id):
        """Prepare data for performance summary view
        
        Args:
            data (dict): Data dictionary
            race_id (str): Race ID
            
        Returns:
            dict: Performance summary data
        """
        # Get race results
        race_results = data.get('race_results', None)
        if race_results is None:
            return {}
            
        race_results_filtered = race_results[race_results['RaceID'] == race_id]
        
        # Get player results
        player_results = data.get('player_results', None)
        if player_results is None:
            return {}
            
        player_results_filtered = player_results[player_results['RaceID'] == race_id]
        
        # Get player names
        player_picks = data.get('player_picks', None)
        player_names = {}
        
        if player_picks is not None:
            for player_id in player_results_filtered['PlayerID'].unique():
                player_rows = player_picks[player_picks['PlayerID'] == player_id]
                if not player_rows.empty:
                    player_names[player_id] = player_rows['PlayerName'].iloc[0]
        
        # Get driver names
        drivers = data.get('drivers', None)
        driver_names = {}
        
        if drivers is not None:
            for driver_id in race_results_filtered['DriverID'].unique():
                driver_rows = drivers[drivers['DriverID'] == driver_id]
                if not driver_rows.empty:
                    driver_names[driver_id] = driver_rows['Name'].iloc[0]
        
        # Process driver performance
        driver_performance = []
        
        for _, result in race_results_filtered.iterrows():
            driver_id = result['DriverID']
            driver_name = driver_names.get(driver_id, driver_id)
            points = result['Points']
            
            driver_performance.append({
                'driver_id': driver_id,
                'name': f"{driver_name} ({driver_id})",
                'points': points
            })
        
        # Process player performance
        player_performance = []
        
        for _, result in player_results_filtered.iterrows():
            player_id = result['PlayerID']
            player_name = player_names.get(player_id, f"Player {player_id}")
            points = result['Points']
            
            player_performance.append({
                'player_id': player_id,
                'name': player_name,
                'points': points
            })
        
        # Calculate driver delta from season average
        # First, get previous races
        completed_races = data['races'][data['races']['Status'] == 'Completed']['RaceID'].tolist()
        race_index = completed_races.index(race_id)
        previous_races = completed_races[:race_index]
        
        driver_deltas = []
        
        if previous_races:
            previous_results = race_results[race_results['RaceID'].isin(previous_races)]
            
            for driver_id in race_results_filtered['DriverID'].unique():
                driver_name = driver_names.get(driver_id, driver_id)
                
                # Calculate average points from previous races
                driver_history = previous_results[previous_results['DriverID'] == driver_id]
                avg_points = driver_history['Points'].mean() if not driver_history.empty else 0
                
                # Get current race points
                current_result = race_results_filtered[race_results_filtered['DriverID'] == driver_id]
                current_points = current_result.iloc[0]['Points'] if not current_result.empty else 0
                
                # Calculate delta
                delta = current_points - avg_points
                
                driver_deltas.append({
                    'driver_id': driver_id,
                    'name': f"{driver_name} ({driver_id})",
                    'avg_points': avg_points,
                    'current_points': current_points,
                    'delta': delta
                })
        
        # Find most impactful driver performances
        impactful_drivers = []
        
        for _, result in player_results_filtered.iterrows():
            player_id = result['PlayerID']
            player_name = player_names.get(player_id, f"Player {player_id}")
            
            if 'CalculationDetails' in result and not pd.isna(result['CalculationDetails']):
                details = result['CalculationDetails']
                parts = details.split(',')
                
                for part in parts:
                    part = part.strip()
                    if ':' in part:
                        driver_part, points_str = part.split(':', 1)
                        driver_id = driver_part.strip().split()[0]
                        driver_name = driver_names.get(driver_id, driver_id)
                        
                        try:
                            points = float(points_str.strip())
                        except ValueError:
                            # Extract number
                            import re
                            matches = re.findall(r'-?\d+(?:\.\d+)?', points_str)
                            points = float(matches[0]) if matches else 0
                        
                        # Only include significant impacts
                        if abs(points) >= 5:
                            impactful_drivers.append({
                                'player_id': player_id,
                                'player_name': player_name,
                                'driver_id': driver_id,
                                'driver_name': driver_name,
                                'points': points
                            })
        
        # Return all data
        return {
            'driver_performance': driver_performance,
            'player_performance': player_performance,
            'driver_deltas': driver_deltas,
            'impactful_drivers': impactful_drivers
        }
    
    def prepare_fantasy_impact_events(self, data, race_id):
        """Prepare data for fantasy impact events view
        
        Args:
            data (dict): Data dictionary
            race_id (str): Race ID
            
        Returns:
            dict: Fantasy impact events data
        """
        # Get race results
        race_results = data.get('race_results', None)
        if race_results is None:
            return {}
            
        race_results_filtered = race_results[race_results['RaceID'] == race_id]
        
        # Get driver data
        drivers = data.get('drivers', None)
        if drivers is None:
            return {}
        
        # Get player results
        player_results = data.get('player_results', None)
        if player_results is None:
            return {}
            
        player_results_filtered = player_results[player_results['RaceID'] == race_id]
        
        # Get player names
        player_picks = data.get('player_picks', None)
        player_names = {}
        
        if player_picks is not None:
            for player_id in player_results_filtered['PlayerID'].unique():
                player_rows = player_picks[player_picks['PlayerID'] == player_id]
                if not player_rows.empty:
                    player_names[player_id] = player_rows['PlayerName'].iloc[0]
        
        # Get driver names
        driver_names = {}
        
        if drivers is not None:
            for driver_id in race_results_filtered['DriverID'].unique():
                driver_rows = drivers[drivers['DriverID'] == driver_id]
                if not driver_rows.empty:
                    driver_names[driver_id] = driver_rows['Name'].iloc[0]
        
        # Calculate value drivers (points per credit)
        value_drivers = []
        
        for _, row in race_results_filtered.iterrows():
            driver_id = row['DriverID']
            points = row['Points']
            
            driver_row = drivers[drivers['DriverID'] == driver_id]
            if not driver_row.empty:
                driver_name = driver_row.iloc[0]['Name']
                credits = driver_row.iloc[0]['Credits']
                
                if credits > 0:  # Avoid division by zero
                    efficiency = points / credits
                    
                    value_drivers.append({
                        'driver_id': driver_id,
                        'name': driver_name,
                        'points': points,
                        'credits': credits,
                        'efficiency': efficiency
                    })
        
        # Separate best value and underperforming drivers
        best_value_drivers = [d for d in value_drivers if d['efficiency'] > 0]
        underperforming_drivers = [d for d in value_drivers if d['efficiency'] <= 2]
        
        # Sort by efficiency
        best_value_drivers.sort(key=lambda x: x['efficiency'], reverse=True)
        underperforming_drivers.sort(key=lambda x: x['efficiency'])
        
        # Calculate team performance
        team_performance = []
        
        if 'teams' in data:
            teams = data['teams']
            driver_teams = {row['DriverID']: row['DefaultTeam'] for _, row in drivers.iterrows()}
            
            # Group driver points by team
            team_points = {}
            for _, result in race_results_filtered.iterrows():
                driver_id = result['DriverID']
                points = result['Points']
                
                # Get driver's team
                team_id = driver_teams.get(driver_id)
                if team_id:
                    if team_id in team_points:
                        team_points[team_id] += points
                    else:
                        team_points[team_id] = points
            
            # Format team data
            for team_id, points in team_points.items():
                team_row = teams[teams['TeamID'] == team_id]
                if not team_row.empty:
                    team_name = team_row.iloc[0]['Name']
                    
                    team_performance.append({
                        'team_id': team_id,
                        'name': team_name,
                        'points': points
                    })
            
            # Sort by points
            team_performance.sort(key=lambda x: x['points'], reverse=True)
        
        # Calculate driver point gaps for each player
        player_driver_gaps = {'players': [], 'driver1_values': [], 'driver2_values': [], 
                            'driver1_labels': [], 'driver2_labels': []}
        
        for player_id in player_results_filtered['PlayerID'].unique():
            player_name = player_names.get(player_id, f"Player {player_id}")
            
            result = player_results_filtered[player_results_filtered['PlayerID'] == player_id]
            
            if not result.empty and 'CalculationDetails' in result.iloc[0]:
                details = result.iloc[0]['CalculationDetails']
                if not pd.isna(details):
                    driver_points = {}
                    
                    # Parse calculation details
                    parts = details.split(',')
                    for part in parts:
                        part = part.strip()
                        if ':' in part:
                            driver_id, points_str = part.split(':', 1)
                            driver_id = driver_id.strip().split()[0]
                            
                            try:
                                points = float(points_str.strip())
                            except ValueError:
                                # Extract number
                                import re
                                matches = re.findall(r'-?\d+(?:\.\d+)?', points_str)
                                points = float(matches[0]) if matches else 0
                            
                            driver_points[driver_id] = points
                    
                    # Get top 2 drivers by absolute points
                    if driver_points:
                        sorted_drivers = sorted(driver_points.items(), key=lambda x: abs(x[1]), reverse=True)
                        
                        if len(sorted_drivers) >= 2:
                            # Add to data
                            player_driver_gaps['players'].append(player_name)
                            player_driver_gaps['driver1_values'].append(sorted_drivers[0][1])
                            player_driver_gaps['driver2_values'].append(sorted_drivers[1][1])
                            player_driver_gaps['driver1_labels'].append(sorted_drivers[0][0])
                            player_driver_gaps['driver2_labels'].append(sorted_drivers[1][0])
        
        # Team colors
        team_colors = {
            'RBR': '#00007D',  # Dark blue
            'FER': '#DC0000',  # Red
            'MER': '#00D2BE',  # Teal
            'MCL': '#FF8700',  # Orange
            'AST': '#006F62',  # Green
            'ALP': '#0090FF',  # Blue
            'HAS': '#787878',  # Gray
            'RBT': '#1E41FF',  # Royal blue
            'WIL': '#0082FA',  # Light blue
            'SAU': '#900000'   # Burgundy
        }
        
        # Return all data with scale parameters
        return {
            'best_value_drivers': best_value_drivers,
            'underperforming_drivers': underperforming_drivers,
            'team_performance': team_performance,
            'player_driver_gaps': player_driver_gaps,
            'team_colors': team_colors,
            'value_scale_max': 17,
            'underp_scale_min': -22,
            'underp_scale_max': 3,
            'team_scale_min': -25,
            'team_scale_max': 70,
            'gap_scale_min': -25,
            'gap_scale_max': 65
        }
    
    def prepare_player_standings_impact(self, data, race_id):
        """Prepare data for player standings impact view
        
        Args:
            data (dict): Data dictionary
            race_id (str): Race ID
            
        Returns:
            dict: Player standings impact data
        """
        # Get all races up to the current one
        races = data.get('races', None)
        if races is None:
            return {}
            
        completed_races = races[races['Status'] == 'Completed']['RaceID'].tolist()
        if race_id not in completed_races:
            return {}
            
        race_index = completed_races.index(race_id)
        previous_races = completed_races[:race_index]
        
        # Get player results
        player_results = data.get('player_results', None)
        if player_results is None:
            return {}
            
        current_race_results = player_results[player_results['RaceID'] == race_id]
        
        # Get player names
        player_picks = data.get('player_picks', None)
        player_names = {}
        
        if player_picks is not None:
            for player_id in player_results['PlayerID'].unique():
                player_rows = player_picks[player_picks['PlayerID'] == player_id]
                if not player_rows.empty:
                    player_names[player_id] = player_rows['PlayerName'].iloc[0]
        
        # Calculate standings before this race
        pre_race_standings = {}
        
        if previous_races:
            prev_results = player_results[player_results['RaceID'].isin(previous_races)]
            
            for player_id in player_results['PlayerID'].unique():
                player_prev = prev_results[prev_results['PlayerID'] == player_id]
                total_points = player_prev['Points'].sum()
                pre_race_standings[player_id] = total_points
        else:
            # If this is the first race, all players start at 0
            for player_id in player_results['PlayerID'].unique():
                pre_race_standings[player_id] = 0
        
        # Calculate standings after this race
        post_race_standings = pre_race_standings.copy()
        
        # Add current race points
        for _, result in current_race_results.iterrows():
            player_id = result['PlayerID']
            points = result['Points']
            
            if player_id in post_race_standings:
                post_race_standings[player_id] += points
            else:
                post_race_standings[player_id] = points
        
        # Calculate positions
        pre_race_positions = {player_id: i+1 for i, (player_id, _) in 
                            enumerate(sorted(pre_race_standings.items(), key=lambda x: x[1], reverse=True))}
        post_race_positions = {player_id: i+1 for i, (player_id, _) in 
                            enumerate(sorted(post_race_standings.items(), key=lambda x: x[1], reverse=True))}
        
        # Calculate position changes
        position_changes = []
        for player_id in set(pre_race_positions.keys()) | set(post_race_positions.keys()):
            player_name = player_names.get(player_id, f"Player {player_id}")
            
            pre_pos = pre_race_positions.get(player_id, len(pre_race_positions) + 1)
            post_pos = post_race_positions.get(player_id, len(post_race_positions) + 1)
            
            if race_index == 0:  # First race, no position change
                pos_delta = 0
            else:
                pos_delta = pre_pos - post_pos  # Positive = moved up
            
            position_changes.append({
                'player_id': player_id,
                'player_name': player_name,
                'pre_position': pre_pos,
                'post_position': post_pos,
                'position_delta': pos_delta
            })
        
        # Sort by position delta (largest first)
        position_changes.sort(key=lambda x: x['position_delta'], reverse=True)
        
        # Race points for this race
        race_points = []
        for player_id in set(pre_race_standings.keys()) | set(post_race_standings.keys()):
            player_name = player_names.get(player_id, f"Player {player_id}")
            
            # Get points for this race
            player_race = current_race_results[current_race_results['PlayerID'] == player_id]
            points = player_race.iloc[0]['Points'] if not player_race.empty else 0
            
            race_points.append({
                'player_id': player_id,
                'player_name': player_name,
                'points': points
            })
        
        # Sort by points (highest first)
        race_points.sort(key=lambda x: x['points'], reverse=True)
        
        # Prepare standings table
        table_data = []
        column_labels = ['Position', 'Player', 'Previous Pos', 'Previous Pts', 
                        f'{race_id}\nPoints', 'Total Points', 'Change']
        
        # Sort by post-race standing (highest first)
        sorted_players = sorted(post_race_standings.items(), key=lambda x: x[1], reverse=True)
        
        for i, (player_id, post_points) in enumerate(sorted_players):
            player_name = player_names.get(player_id, f"Player {player_id}")
            pre_points = pre_race_standings.get(player_id, 0)
            race_pts = post_points - pre_points
            pre_pos = pre_race_positions.get(player_id, 'N/A') if race_index > 0 else 'N/A'
            post_pos = i + 1
            pos_change = pre_pos - post_pos if isinstance(pre_pos, int) else 'N/A'
            
            table_data.append([
                post_pos,
                player_name,
                pre_pos,
                pre_points if race_index > 0 else 'N/A',
                race_pts,
                post_points,
                pos_change
            ])
        
        # Column widths for table display
        col_widths = [0.1, 0.3, 0.15, 0.15, 0.1, 0.15, 0.1]
        
        # Prepare standings table data
        standings_table = {
            'column_labels': column_labels,
            'table_data': table_data,
            'col_widths': col_widths
        }
        
        # Return all data
        return {
            'position_changes': position_changes,
            'race_points': race_points,
            'standings_table': standings_table
        }

class PlayerDriverPointsController:
    """Controller for Player Driver Points visualization"""
    
    def __init__(self, view, data_manager):
        """
        Initialize the controller.
        
        Args:
            view: The visualization view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        # Initialize view
        self.initialize()
    
    def initialize(self):
        """Initialize the visualization"""
        # Load data
        data = self.data_manager.load_data()
        if not data:
            self.view.show_placeholder("No data available")
            return
            
        # Get race options for dropdown
        races = data.get('races', None)
        if races is None:
            self.view.show_placeholder("No race data available")
            return
            
        # Get completed races
        races = races.sort_values(by='Date')
        completed_races = races[races['Status'] == 'Completed']
        
        race_options = []
        for _, race in completed_races.iterrows():
            race_id = race['RaceID']
            race_name = race['Name']
            race_options.append(f"{race_id} - {race_name}")
        
        # Update view with race options
        self.view.set_race_options(race_options)
        
        # Show placeholder
        self.view.show_placeholder("Select a race and click 'Update Chart'")
    
    def update_visualization(self, race_id):
        """Update the visualization with new data
        
        Args:
            race_id (str): Selected race ID or "All Races"
        """
        try:
            # Load data
            data = self.data_manager.load_data()
            if not data:
                self.view.show_placeholder("No data available")
                return
                
            races = data.get('races', None)
            if races is None:
                self.view.show_placeholder("No race data available")
                return
                
            completed_races = races[races['Status'] == 'Completed']['RaceID'].tolist()
            
            if not completed_races:
                self.view.show_placeholder("No completed races found")
                return
            
            # Process data differently based on selected race
            if race_id == "All Races":
                # Process data for all races combined
                player_data = self.process_all_races_data(data, completed_races)
                note = ""
            else:
                # Process data for a single race
                race_info = races[races['RaceID'] == race_id]
                if race_info.empty:
                    self.view.show_placeholder(f"Race {race_id} not found")
                    return
                    
                race_name = race_info.iloc[0]['Name']
                race_date = race_info.iloc[0]['Date']
                
                # Filter for selected race
                race_results_filtered = data['race_results'][data['race_results']['RaceID'] == race_id]
                player_results_filtered = data['player_results'][data['player_results']['RaceID'] == race_id]
                
                player_data = self.process_single_race_data(race_date, race_results_filtered, 
                                                          player_results_filtered, data['player_picks'], 
                                                          data['drivers'])
                note = ""
            
            # Check if we have any player data
            if not player_data:
                self.view.show_placeholder("No player data found for selected race(s)")
                return
            
            # Check if there are any negative point values
            has_negative = any(player['driver1']['points'] < 0 or player['driver2']['points'] < 0 
                           for player in player_data)
            
            # Prepare data for visualization
            viz_data = {
                'race_id': race_id,
                'race_name': race_info.iloc[0]['Name'] if race_id != "All Races" else "",
                'has_negative': has_negative,
                'player_data': player_data,
                'note': note
            }
            
            # Update the view
            self.view.update(viz_data)
        except Exception as e:
            logger.error(f"Error in PlayerDriverPointsController.update_visualization: {e}")
            self.view.show_placeholder(f"Error generating visualization: {str(e)}")
    
    def process_single_race_data(self, race_date, race_results, player_results, player_picks, drivers):
        """Process data for a single race visualization
        
        Args:
            race_date: The date of the race
            race_results: DataFrame with race results filtered for the selected race
            player_results: DataFrame with player results filtered for the selected race
            player_picks: DataFrame with player picks
            drivers: DataFrame with driver information
            
        Returns:
            list: List of dictionaries with player data
        """
        player_data = []
        
        for _, player_result in player_results.iterrows():
            player_id = player_result['PlayerID']
            total_points = player_result['Points']  # Per-race points
            
            # Get player name
            player_name = player_picks[player_picks['PlayerID'] == player_id]['PlayerName'].values[0] if not player_picks[player_picks['PlayerID'] == player_id].empty else f"Player {player_id}"
            
            # Get drivers for this player at race date
            player_drivers = player_picks[
                (player_picks['PlayerID'] == player_id) & 
                (player_picks['FromDate'] <= race_date) & 
                ((player_picks['ToDate'] >= race_date) | (player_picks['ToDate'].isna()))
            ]
            
            if len(player_drivers) != 2:
                # Skip players without exactly 2 drivers
                continue
                
            driver_data = []
            for _, pick in player_drivers.iterrows():
                driver_id = pick['DriverID']
                driver_result = race_results[race_results['DriverID'] == driver_id]
                
                if not driver_result.empty:
                    driver_points = driver_result.iloc[0]['Points']  # Per-race points
                else:
                    driver_points = 0
                
                driver_name = drivers[drivers['DriverID'] == driver_id]['Name'].values[0] if not drivers[drivers['DriverID'] == driver_id].empty else driver_id
                
                driver_data.append({
                    'id': driver_id,
                    'name': driver_name,
                    'points': driver_points
                })
            
            # Sort drivers by points (higher first)
            driver_data.sort(key=lambda x: x['points'], reverse=True)
            
            player_data.append({
                'player': player_name,
                'driver1': driver_data[0],
                'driver2': driver_data[1],
                'totalPoints': total_points
            })
        
        # Sort by total points (descending)
        player_data.sort(key=lambda x: x['totalPoints'], reverse=True)
        
        return player_data
        
    def process_all_races_data(self, data, completed_races):
        """Process data for all races combined visualization
        
        Args:
            data: Dictionary containing all loaded dataframes
            completed_races: List of completed race IDs
            
        Returns:
            list: List of dictionaries with player data
        """
        # Get unique players
        players = data['player_results']['PlayerID'].unique()
        
        # Create player name dictionary for lookup
        player_names_dict = {}
        if 'player_picks' in data:
            for _, row in data['player_picks'].iterrows():
                player_names_dict[row['PlayerID']] = row['PlayerName']
        
        # Sort races chronologically
        race_dates = {race_id: data['races'][data['races']['RaceID'] == race_id]['Date'].iloc[0] 
                    for race_id in completed_races}
        sorted_races = sorted(completed_races, key=lambda r: race_dates[r])
        
        player_data = []
        # Track positions from previous race for position changes
        prev_positions = {}
        
        for player_id in players:
            # Get player name safely
            player_name = player_names_dict.get(player_id, f"Player {player_id}")
            
            # Get player's total points across all races (sum of per-race points)
            player_total = data['player_results'][data['player_results']['PlayerID'] == player_id]['Points'].sum()
            
            # Get points by driver across all races
            driver_totals = {}
            
            for race_id in sorted_races:
                race_date = data['races'][data['races']['RaceID'] == race_id]['Date'].iloc[0]
                
                # Get drivers for this player at this race date
                player_drivers = data['player_picks'][
                    (data['player_picks']['PlayerID'] == player_id) & 
                    (data['player_picks']['FromDate'] <= race_date) & 
                    ((data['player_picks']['ToDate'] >= race_date) | (data['player_picks']['ToDate'].isna()))
                ]
                
                # Skip if we don't have exactly 2 drivers
                if len(player_drivers) != 2:
                    continue
                
                # Get points for each driver
                for _, pick in player_drivers.iterrows():
                    driver_id = pick['DriverID']
                    
                    # Get driver's points for this race
                    driver_result = data['race_results'][
                        (data['race_results']['RaceID'] == race_id) & 
                        (data['race_results']['DriverID'] == driver_id)
                    ]
                    
                    if not driver_result.empty:
                        points = driver_result.iloc[0]['Points']  # Per-race points
                        
                        # Add to driver's total
                        if driver_id in driver_totals:
                            driver_totals[driver_id]['points'] += points
                        else:
                            driver_name = data['drivers'][data['drivers']['DriverID'] == driver_id]['Name'].values[0] if not data['drivers'][data['drivers']['DriverID'] == driver_id].empty else driver_id
                            driver_totals[driver_id] = {
                                'id': driver_id,
                                'name': driver_name,
                                'points': points
                            }
            
            # Make sure we have driver data
            if not driver_totals:
                continue
            
            # Convert driver totals to list and sort by points
            driver_list = list(driver_totals.values())
            driver_list.sort(key=lambda x: x['points'], reverse=True)
            
            # Make sure we have at least 2 drivers
            while len(driver_list) < 2:
                driver_list.append({
                    'id': 'N/A',
                    'name': 'No Driver',
                    'points': 0
                })
            
            # Take top 2 drivers by points
            player_data.append({
                'player': player_name,
                'player_id': player_id,  # Store player_id in the data
                'driver1': driver_list[0],
                'driver2': driver_list[1] if len(driver_list) > 1 else {'id': 'N/A', 'name': 'No Driver', 'points': 0},
                'totalPoints': player_total,
                'previousPosition': prev_positions.get(player_id, 'N/A'),
                'positionChange': 0  # Will be calculated after sorting
            })
        
        # Sort by total points (highest first)
        player_data.sort(key=lambda x: x['totalPoints'], reverse=True)
        
        # Calculate position changes
        for i, player in enumerate(player_data):
            current_position = i + 1
            previous_position = player['previousPosition']
            
            if previous_position != 'N/A':
                player['positionChange'] = previous_position - current_position
            
            # Store current position for next time
            prev_positions[player['player_id']] = current_position
        
        return player_data