"""
controllers/visualization_controller.py - Controllers for visualizations
"""

import logging

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