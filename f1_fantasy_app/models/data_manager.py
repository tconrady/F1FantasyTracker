"""
models/data_manager.py - Core data model that handles loading, processing, and saving data
"""

import pandas as pd
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('f1_fantasy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class F1DataManager:
    """
    Central data manager class that handles all data operations for the F1 Fantasy application.
    This class is responsible for:
    - Loading data from Excel
    - Processing raw data (converting cumulative to per-race points)
    - Providing access to all data entities
    - Saving data back to Excel
    """
    
    def __init__(self, excel_file):
        """
        Initialize the data manager with the Excel file path.
        
        Args:
            excel_file (str): Path to the Excel file containing F1 Fantasy data
        """
        self.excel_file = excel_file
        
        # Define sheet names
        self.sheet_names = {
            'RACES': 'Races',
            'DRIVERS': 'Drivers',
            'TEAMS': 'Teams',
            'PLAYER_PICKS': 'PlayerPicks',
            'DRIVER_ASSIGNMENTS': 'DriverAssignments',
            'RACE_RESULTS': 'RaceResults',
            'PLAYER_RESULTS': 'PlayerResults'
        }
        
        # Data cache
        self.data_cache = {}
        self.raw_data_cache = {}
        self.is_cache_valid = False
        
    def _check_excel_access(self) -> bool:
        """Check if the Excel file is accessible for read/write operations."""
        try:
            # Try opening the file for read/write
            if os.path.exists(self.excel_file):
                with open(self.excel_file, 'r+') as f:
                    pass
                return True
            else:
                logger.warning(f"Excel file {self.excel_file} does not exist")
                return False
        except IOError as e:
            logger.error(f"Cannot access Excel file {self.excel_file}: {e}")
            return False
    
    def create_excel_if_not_exists(self) -> bool:
        """Create the Excel file with required sheets if it doesn't exist."""
        if os.path.exists(self.excel_file):
            logger.info(f"Excel file {self.excel_file} already exists.")
            return True
        
        try:
            logger.info(f"Creating new Excel file {self.excel_file} with required sheets.")
            
            # Create empty DataFrames for each sheet with appropriate columns
            df_races = pd.DataFrame(columns=['RaceID', 'Name', 'Date', 'Status'])
            df_drivers = pd.DataFrame(columns=['DriverID', 'Name', 'DefaultTeam', 'Credits'])
            df_teams = pd.DataFrame(columns=['TeamID', 'Name'])
            df_player_picks = pd.DataFrame(columns=['PlayerID', 'PlayerName', 'DriverID', 'FromDate', 'ToDate'])
            df_driver_assignments = pd.DataFrame(columns=['RaceID', 'DriverID', 'TeamID', 'SubstitutedForDriverID'])
            df_race_results = pd.DataFrame(columns=['RaceID', 'DriverID', 'Points'])
            df_player_results = pd.DataFrame(columns=['RaceID', 'PlayerID', 'Points', 'CalculationDetails'])
            
            # Create Excel writer and save all DataFrames to their respective sheets
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                df_races.to_excel(writer, sheet_name=self.sheet_names['RACES'], index=False)
                df_drivers.to_excel(writer, sheet_name=self.sheet_names['DRIVERS'], index=False)
                df_teams.to_excel(writer, sheet_name=self.sheet_names['TEAMS'], index=False)
                df_player_picks.to_excel(writer, sheet_name=self.sheet_names['PLAYER_PICKS'], index=False)
                df_driver_assignments.to_excel(writer, sheet_name=self.sheet_names['DRIVER_ASSIGNMENTS'], index=False)
                df_race_results.to_excel(writer, sheet_name=self.sheet_names['RACE_RESULTS'], index=False)
                df_player_results.to_excel(writer, sheet_name=self.sheet_names['PLAYER_RESULTS'], index=False)
            
            logger.info(f"Excel file {self.excel_file} created successfully with all required sheets.")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Excel file: {e}")
            return False
    
    def initialize_season_data(self, season_year=2025) -> bool:
        """
        Initialize the Excel file with default season data.
        
        Args:
            season_year (int): Season year
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                # 2025 F1 Race Calendar
                races_data = [
                    {'RaceID': 'AUS', 'Name': 'Australian Grand Prix', 'Date': '2025-03-16', 'Status': 'Upcoming'},
                    {'RaceID': 'CHN', 'Name': 'Chinese Grand Prix', 'Date': '2025-03-23', 'Status': 'Upcoming'},
                    {'RaceID': 'JPN', 'Name': 'Japanese Grand Prix', 'Date': '2025-04-06', 'Status': 'Upcoming'},
                    {'RaceID': 'BHR', 'Name': 'Bahrain Grand Prix', 'Date': '2025-04-13', 'Status': 'Upcoming'},
                    {'RaceID': 'SAU', 'Name': 'Saudi Arabian Grand Prix', 'Date': '2025-04-20', 'Status': 'Upcoming'},
                    {'RaceID': 'MIA', 'Name': 'Miami Grand Prix', 'Date': '2025-05-04', 'Status': 'Upcoming'},
                    {'RaceID': 'EMR', 'Name': 'Emilia Romagna Grand Prix', 'Date': '2025-05-18', 'Status': 'Upcoming'},
                    {'RaceID': 'MON', 'Name': 'Monaco Grand Prix', 'Date': '2025-05-25', 'Status': 'Upcoming'},
                    {'RaceID': 'ESP', 'Name': 'Spanish Grand Prix', 'Date': '2025-06-01', 'Status': 'Upcoming'},
                    {'RaceID': 'CAN', 'Name': 'Canadian Grand Prix', 'Date': '2025-06-15', 'Status': 'Upcoming'},
                    {'RaceID': 'AUT', 'Name': 'Austrian Grand Prix', 'Date': '2025-06-29', 'Status': 'Upcoming'},
                    {'RaceID': 'GBR', 'Name': 'British Grand Prix', 'Date': '2025-07-06', 'Status': 'Upcoming'},
                    {'RaceID': 'BEL', 'Name': 'Belgian Grand Prix', 'Date': '2025-07-27', 'Status': 'Upcoming'},
                    {'RaceID': 'HUN', 'Name': 'Hungarian Grand Prix', 'Date': '2025-08-03', 'Status': 'Upcoming'},
                    {'RaceID': 'NED', 'Name': 'Dutch Grand Prix', 'Date': '2025-08-31', 'Status': 'Upcoming'},
                    {'RaceID': 'ITA', 'Name': 'Italian Grand Prix', 'Date': '2025-09-07', 'Status': 'Upcoming'},
                    {'RaceID': 'AZE', 'Name': 'Azerbaijan Grand Prix', 'Date': '2025-09-21', 'Status': 'Upcoming'},
                    {'RaceID': 'SIN', 'Name': 'Singapore Grand Prix', 'Date': '2025-10-05', 'Status': 'Upcoming'},
                    {'RaceID': 'USA', 'Name': 'United States Grand Prix', 'Date': '2025-10-19', 'Status': 'Upcoming'},
                    {'RaceID': 'MEX', 'Name': 'Mexican Grand Prix', 'Date': '2025-10-26', 'Status': 'Upcoming'},
                    {'RaceID': 'BRA', 'Name': 'Brazilian Grand Prix', 'Date': '2025-11-09', 'Status': 'Upcoming'},
                    {'RaceID': 'LVG', 'Name': 'Las Vegas Grand Prix', 'Date': '2025-11-22', 'Status': 'Upcoming'},
                    {'RaceID': 'QAT', 'Name': 'Qatar Grand Prix', 'Date': '2025-11-30', 'Status': 'Upcoming'},
                    {'RaceID': 'ABU', 'Name': 'Abu Dhabi Grand Prix', 'Date': '2025-12-07', 'Status': 'Upcoming'}
                ]
                df_races = pd.DataFrame(races_data)
                df_races['Date'] = pd.to_datetime(df_races['Date'])
                df_races.to_excel(writer, sheet_name=self.sheet_names['RACES'], index=False)
                
                # 2025 F1 Teams
                teams_data = [
                    {'TeamID': 'RBR', 'Name': 'Red Bull Racing'},
                    {'TeamID': 'FER', 'Name': 'Ferrari'},
                    {'TeamID': 'MER', 'Name': 'Mercedes'},
                    {'TeamID': 'MCL', 'Name': 'McLaren'},
                    {'TeamID': 'AST', 'Name': 'Aston Martin'},
                    {'TeamID': 'ALP', 'Name': 'Alpine'},
                    {'TeamID': 'HAS', 'Name': 'Haas F1 Team'},
                    {'TeamID': 'RBT', 'Name': 'Racing Bulls'},
                    {'TeamID': 'WIL', 'Name': 'Williams'},
                    {'TeamID': 'SAU', 'Name': 'Sauber'}
                ]
                df_teams = pd.DataFrame(teams_data)
                df_teams.to_excel(writer, sheet_name=self.sheet_names['TEAMS'], index=False)
                
                # 2025 F1 Drivers with credit values (1-4)
                drivers_data = [
                    # Top tier (4 credits)
                    {'DriverID': 'VER', 'Name': 'Max Verstappen', 'DefaultTeam': 'RBR', 'Credits': 4},
                    {'DriverID': 'NOR', 'Name': 'Lando Norris', 'DefaultTeam': 'MCL', 'Credits': 4},
                    {'DriverID': 'LEC', 'Name': 'Charles Leclerc', 'DefaultTeam': 'FER', 'Credits': 4},
                    {'DriverID': 'PIA', 'Name': 'Oscar Piastri', 'DefaultTeam': 'MCL', 'Credits': 4},
                    {'DriverID': 'HAM', 'Name': 'Lewis Hamilton', 'DefaultTeam': 'FER', 'Credits': 4},
                    
                    # Second tier (3 credits)
                    {'DriverID': 'RUS', 'Name': 'George Russell', 'DefaultTeam': 'MER', 'Credits': 3},
                    {'DriverID': 'LAW', 'Name': 'Liam Lawson', 'DefaultTeam': 'RBR', 'Credits': 3},
                    {'DriverID': 'ANT', 'Name': 'Andrea Kimi Antonelli', 'DefaultTeam': 'MER', 'Credits': 3},
                    {'DriverID': 'GAS', 'Name': 'Pierre Gasly', 'DefaultTeam': 'ALP', 'Credits': 3},
                    {'DriverID': 'SAI', 'Name': 'Carlos Sainz', 'DefaultTeam': 'WIL', 'Credits': 3},
                    
                    # Third tier (2 credits)
                    {'DriverID': 'ALO', 'Name': 'Fernando Alonso', 'DefaultTeam': 'AST', 'Credits': 2},
                    {'DriverID': 'TSU', 'Name': 'Yuki Tsunoda', 'DefaultTeam': 'RBT', 'Credits': 2},
                    {'DriverID': 'ALB', 'Name': 'Alexander Albon', 'DefaultTeam': 'WIL', 'Credits': 2},
                    {'DriverID': 'HUL', 'Name': 'Nico Hulkenberg', 'DefaultTeam': 'SAU', 'Credits': 2},
                    {'DriverID': 'OCO', 'Name': 'Esteban Ocon', 'DefaultTeam': 'HAS', 'Credits': 2},
                    
                    # Fourth tier (1 credit)
                    {'DriverID': 'STR', 'Name': 'Lance Stroll', 'DefaultTeam': 'AST', 'Credits': 1},
                    {'DriverID': 'BEA', 'Name': 'Oliver Bearman', 'DefaultTeam': 'HAS', 'Credits': 1},
                    {'DriverID': 'DOO', 'Name': 'Jack Doohan', 'DefaultTeam': 'ALP', 'Credits': 1},
                    {'DriverID': 'HAD', 'Name': 'Isack Hadjar', 'DefaultTeam': 'RBT', 'Credits': 1},
                    {'DriverID': 'BOR', 'Name': 'Gabriel Bortoleto', 'DefaultTeam': 'SAU', 'Credits': 1},
                    
                    # Reserve drivers (0 credits since they're not initially picked)
                    {'DriverID': 'ZHO', 'Name': 'Zhou Guanyu', 'DefaultTeam': 'FER', 'Credits': 0},
                    {'DriverID': 'GIO', 'Name': 'Antonio Giovinazzi', 'DefaultTeam': 'FER', 'Credits': 0},
                    {'DriverID': 'BOT', 'Name': 'Valtteri Bottas', 'DefaultTeam': 'MER', 'Credits': 0},
                    {'DriverID': 'VES', 'Name': 'Frederik Vesti', 'DefaultTeam': 'MER', 'Credits': 0},
                    {'DriverID': 'DRU', 'Name': 'Felipe Drugovich', 'DefaultTeam': 'AST', 'Credits': 0},
                    {'DriverID': 'ARO', 'Name': 'Paul Aron', 'DefaultTeam': 'ALP', 'Credits': 0},
                    {'DriverID': 'HIR', 'Name': 'Ryo Hirakawa', 'DefaultTeam': 'ALP', 'Credits': 0},
                    {'DriverID': 'COL', 'Name': 'Franco Colapinto', 'DefaultTeam': 'ALP', 'Credits': 0},
                    {'DriverID': 'TUR', 'Name': 'Oliver Turvey', 'DefaultTeam': 'WIL', 'Credits': 0}
                ]
                df_drivers = pd.DataFrame(drivers_data)
                df_drivers.to_excel(writer, sheet_name=self.sheet_names['DRIVERS'], index=False)
                
            logger.info(f"Season {season_year} data initialized successfully.")
            self.is_cache_valid = False  # Force reload on next data request
            return True
        except Exception as e:
            logger.error(f"Error initializing season data: {e}")
            return False
    
    def _load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load raw data from Excel file without processing.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing raw dataframes for each sheet
        """
        if not self._check_excel_access():
            return {}
        
        try:
            # Load all required sheets
            data = {}
            
            data['races'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['RACES'])
            data['drivers'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['DRIVERS'])
            data['teams'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['TEAMS'])
            data['player_picks'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['PLAYER_PICKS'])
            data['driver_assignments'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['DRIVER_ASSIGNMENTS'])
            data['race_results'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['RACE_RESULTS'])
            data['player_results'] = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['PLAYER_RESULTS'])
            
            # Convert dates
            data['races']['Date'] = pd.to_datetime(data['races']['Date'])
            if 'FromDate' in data['player_picks'].columns:
                data['player_picks']['FromDate'] = pd.to_datetime(data['player_picks']['FromDate'])
            if 'ToDate' in data['player_picks'].columns:
                data['player_picks']['ToDate'] = pd.to_datetime(data['player_picks']['ToDate'])
            
            logger.info(f"Raw data loaded successfully from {self.excel_file}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading raw data: {e}")
            return {}
    
    def _process_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Process raw data to create additional calculated fields.
        - Convert cumulative race points to per-race points
        - Handle substitutions
        - Calculate other derived data
        
        Args:
            raw_data (Dict[str, pd.DataFrame]): Raw data loaded from Excel
            
        Returns:
            Dict[str, pd.DataFrame]: Processed data
        """
        if not raw_data:
            return {}
        
        # Create a copy to avoid modifying the original
        processed_data = {key: df.copy() for key, df in raw_data.items()}
        
        # Get completed races sorted by date
        completed_races = processed_data['races'][processed_data['races']['Status'] == 'Completed']
        completed_races = completed_races.sort_values(by='Date')
        completed_race_ids = completed_races['RaceID'].tolist()
        
        if completed_race_ids:
            # Store original data
            processed_data['original_race_results'] = processed_data['race_results'].copy()
            processed_data['original_player_results'] = processed_data['player_results'].copy()
            
            # Process driver race results - convert cumulative to per-race points
            per_race_driver_results = []
            
            # Process each driver
            for driver_id in processed_data['drivers']['DriverID'].unique():
                # Get driver results
                driver_results = processed_data['original_race_results'][
                    processed_data['original_race_results']['DriverID'] == driver_id
                ]
                
                # Map race ID to points
                cumulative_points_map = {}
                for _, row in driver_results.iterrows():
                    cumulative_points_map[row['RaceID']] = row['Points']
                
                # Calculate per-race points
                prev_points = 0
                for race_id in completed_race_ids:
                    if race_id in cumulative_points_map:
                        current_points = cumulative_points_map[race_id]
                        race_points = current_points - prev_points
                        prev_points = current_points
                    else:
                        race_points = 0
                        
                    per_race_driver_results.append({
                        'RaceID': race_id,
                        'DriverID': driver_id,
                        'Points': race_points,
                        'CumulativePoints': prev_points
                    })
            
            # Replace race_results with per-race version
            if per_race_driver_results:
                processed_data['race_results'] = pd.DataFrame(per_race_driver_results)
            
            # Process player results - convert cumulative to per-race points
            per_race_player_results = []
            
            # Process each player
            for player_id in processed_data['original_player_results']['PlayerID'].unique():
                # Get player results
                player_results = processed_data['original_player_results'][
                    processed_data['original_player_results']['PlayerID'] == player_id
                ]
                
                # Map race ID to data
                player_data_map = {}
                for _, row in player_results.iterrows():
                    player_data_map[row['RaceID']] = {
                        'Points': row['Points'],
                        'CalculationDetails': row['CalculationDetails'] if 'CalculationDetails' in row else ""
                    }
                
                # Calculate per-race points
                prev_points = 0
                for race_id in completed_race_ids:
                    if race_id in player_data_map:
                        current_points = player_data_map[race_id]['Points']
                        calc_details = player_data_map[race_id]['CalculationDetails']
                        race_points = current_points - prev_points
                        prev_points = current_points
                    else:
                        race_points = 0
                        calc_details = ""
                        
                    # Create new calculation details if available
                    new_calc_details = self._regenerate_calculation_details(
                        race_id, 
                        calc_details, 
                        processed_data['race_results']
                    )
                    
                    per_race_player_results.append({
                        'RaceID': race_id,
                        'PlayerID': player_id,
                        'Points': race_points,
                        'CumulativePoints': prev_points,
                        'CalculationDetails': new_calc_details
                    })
            
            # Replace player_results with per-race version
            if per_race_player_results:
                processed_data['player_results'] = pd.DataFrame(per_race_player_results)
        
        logger.info("Data processed successfully with per-race points calculated")
        return processed_data
    
    def _regenerate_calculation_details(self, race_id, original_details, race_results_df):
        """
        Regenerate calculation details based on per-race points.
        
        Args:
            race_id (str): Race ID
            original_details (str): Original calculation details
            race_results_df (pd.DataFrame): DataFrame with per-race points
            
        Returns:
            str: Updated calculation details
        """
        if not original_details:
            return ""
        
        # Parse original details to extract driver IDs
        new_calc_parts = []
        
        for part in original_details.split(','):
            part = part.strip()
            if ':' in part:
                # Extract driver ID
                driver_part = part.split(':', 1)[0].strip()
                driver_id = driver_part.split()[0] if ' ' in driver_part else driver_part
                
                # Find the per-race points for this driver
                driver_race_result = race_results_df[
                    (race_results_df['RaceID'] == race_id) & 
                    (race_results_df['DriverID'] == driver_id)
                ]
                
                if not driver_race_result.empty:
                    driver_points = driver_race_result.iloc[0]['Points']
                    new_calc_parts.append(f"{driver_part}: {driver_points:.1f}")
        
        return ", ".join(new_calc_parts)
    
    def load_data(self, refresh=False) -> Dict[str, pd.DataFrame]:
        """
        Load and process all data from Excel file.
        Uses caching to improve performance.
        
        Args:
            refresh (bool): Force refresh cache
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing processed dataframes
        """
        if refresh or not self.is_cache_valid or not self.data_cache:
            # Load raw data
            self.raw_data_cache = self._load_raw_data()
            
            # Process data
            if self.raw_data_cache:
                self.data_cache = self._process_data(self.raw_data_cache)
                self.is_cache_valid = True
            else:
                self.data_cache = {}
                self.is_cache_valid = False
        
        return self.data_cache
    
    def add_player(self, player_id, player_name, driver_ids):
        """
        Add a new player with driver picks.
        
        Args:
            player_id (str): Player ID
            player_name (str): Player name
            driver_ids (list): List of driver IDs
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Load existing player picks
            df_player_picks = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['PLAYER_PICKS'])
            
            # Create new player picks
            from_date = datetime.now().strftime('%Y-%m-%d')
            new_picks = []
            for driver_id in driver_ids:
                new_picks.append({
                    'PlayerID': player_id,
                    'PlayerName': player_name,
                    'DriverID': driver_id,
                    'FromDate': from_date,
                    'ToDate': None  # Open-ended, until changed
                })
            
            # Append new picks to DataFrame
            df_player_picks = pd.concat([df_player_picks, pd.DataFrame(new_picks)], ignore_index=True)
            
            # Save updated picks
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_player_picks.to_excel(writer, sheet_name=self.sheet_names['PLAYER_PICKS'], index=False)
            
            logger.info(f"Player {player_name} added with {len(driver_ids)} driver picks.")
            self.is_cache_valid = False  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"Error adding player: {e}")
            return False
    
    def update_player_pick(self, player_id, old_driver_id, new_driver_id):
        """
        Update a player's driver pick.
        
        Args:
            player_id (str): Player ID
            old_driver_id (str): Driver ID being replaced
            new_driver_id (str): New driver ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Load existing player picks
            df_player_picks = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['PLAYER_PICKS'])
            
            # Close the old pick by setting ToDate to today
            today = datetime.now().strftime('%Y-%m-%d')
            mask = (df_player_picks['PlayerID'] == player_id) & (df_player_picks['DriverID'] == old_driver_id) & (df_player_picks['ToDate'].isna())
            
            if sum(mask) == 0:
                logger.warning(f"No active pick found for player {player_id} with driver {old_driver_id}")
                return False
                
            df_player_picks.loc[mask, 'ToDate'] = today
            
            # Get player name
            player_name = df_player_picks.loc[mask, 'PlayerName'].values[0] if sum(mask) > 0 else "Unknown"
            
            # Add the new pick
            new_pick = {
                'PlayerID': player_id,
                'PlayerName': player_name,
                'DriverID': new_driver_id,
                'FromDate': today,
                'ToDate': None
            }
            df_player_picks = pd.concat([df_player_picks, pd.DataFrame([new_pick])], ignore_index=True)
            
            # Save updated picks
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_player_picks.to_excel(writer, sheet_name=self.sheet_names['PLAYER_PICKS'], index=False)
            
            logger.info(f"Player {player_id} updated pick from {old_driver_id} to {new_driver_id}.")
            self.is_cache_valid = False  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"Error updating player pick: {e}")
            return False
    
    def record_driver_substitution(self, race_id, substitute_driver_id, team_id, replaced_driver_id):
        """
        Record a driver substitution for a specific race.
        
        Args:
            race_id (str): Race ID
            substitute_driver_id (str): ID of the substitute driver
            team_id (str): Team ID
            replaced_driver_id (str): ID of the driver being replaced
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Load existing driver assignments
            df_assignments = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['DRIVER_ASSIGNMENTS'])
            
            # Check if this substitution already exists
            existing = df_assignments[
                (df_assignments['RaceID'] == race_id) & 
                (df_assignments['DriverID'] == substitute_driver_id) & 
                (df_assignments['TeamID'] == team_id) &
                (df_assignments['SubstitutedForDriverID'] == replaced_driver_id)
            ]
            
            if not existing.empty:
                logger.info(f"This substitution already exists for race {race_id}.")
                return True  # Consider this a success rather than failure
            
            # Add the substitution
            new_assignment = {
                'RaceID': race_id,
                'DriverID': substitute_driver_id,
                'TeamID': team_id,
                'SubstitutedForDriverID': replaced_driver_id
            }
            df_assignments = pd.concat([df_assignments, pd.DataFrame([new_assignment])], ignore_index=True)
            
            # Save updated assignments
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_assignments.to_excel(writer, sheet_name=self.sheet_names['DRIVER_ASSIGNMENTS'], index=False)
            
            logger.info(f"Recorded substitution for race {race_id}: {substitute_driver_id} replacing {replaced_driver_id} at {team_id}.")
            
            # Invalidate cache to ensure fresh data is loaded next time
            self.is_cache_valid = False
            
            # If race is already completed, recalculate points
            races = self.load_data().get('races', pd.DataFrame())
            if not races.empty and race_id in races[races['Status'] == 'Completed']['RaceID'].values:
                self.calculate_player_points_for_race(race_id)
                logger.info(f"Recalculated player points for race {race_id} after substitution.")
            
            return True
            
        except PermissionError:
            logger.error(f"Permission denied when accessing {self.excel_file}. Please close the file if it's open in Excel.")
            return False
        except Exception as e:
            logger.error(f"Error recording driver substitution: {e}")
            return False
    
    def save_race_results(self, race_id, results_data):
        """
        Save race results for a specific race.
        
        Args:
            race_id (str): Race ID
            results_data (list): List of dictionaries with race results
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Create dataframe for race results
            df_results = pd.DataFrame(results_data)
            
            # Load existing results
            try:
                df_existing_results = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['RACE_RESULTS'])
                
                # Remove existing results for this race if any
                df_existing_results = df_existing_results[df_existing_results['RaceID'] != race_id]
                
                # Combine with new results
                df_results = pd.concat([df_existing_results, df_results], ignore_index=True)
            except:
                # No existing results sheet or error loading it
                logger.warning(f"No existing race results found or error loading them. Creating new data.")
            
            # Save updated results
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_results.to_excel(writer, sheet_name=self.sheet_names['RACE_RESULTS'], index=False)
            
            # Update race status to 'Completed'
            df_races = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['RACES'])
            df_races.loc[df_races['RaceID'] == race_id, 'Status'] = 'Completed'
            
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_races.to_excel(writer, sheet_name=self.sheet_names['RACES'], index=False)
            
            logger.info(f"Race results for {race_id} saved successfully.")
            self.is_cache_valid = False  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"Error saving race results: {e}")
            return False
    
    def save_player_results(self, race_id, player_results):
        """
        Save player results for a specific race.
        
        Args:
            race_id (str): Race ID
            player_results (list): List of dictionaries with player results
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Create dataframe for player results
            df_player_results = pd.DataFrame(player_results)
            
            # Load existing player results
            try:
                df_existing_results = pd.read_excel(self.excel_file, sheet_name=self.sheet_names['PLAYER_RESULTS'])
                
                # Remove existing results for this race if any
                df_existing_results = df_existing_results[df_existing_results['RaceID'] != race_id]
                
                # Combine with new results
                df_player_results = pd.concat([df_existing_results, df_player_results], ignore_index=True)
            except:
                # No existing results sheet or error loading it
                logger.warning(f"No existing player results found or error loading them. Creating new data.")
            
            # Save updated results
            with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_player_results.to_excel(writer, sheet_name=self.sheet_names['PLAYER_RESULTS'], index=False)
            
            logger.info(f"Player results for race {race_id} saved successfully.")
            self.is_cache_valid = False  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"Error saving player results: {e}")
            return False
    
    def get_upcoming_races(self):
        """
        Get upcoming races.
        
        Returns:
            pd.DataFrame: DataFrame with upcoming races
        """
        data = self.load_data()
        if not data:
            return pd.DataFrame()
        
        try:
            races = data['races']
            upcoming_races = races[races['Date'] > datetime.now()]
            return upcoming_races.sort_values(by='Date')
        except Exception as e:
            logger.error(f"Error retrieving upcoming races: {e}")
            return pd.DataFrame()
    
    def get_most_recent_race(self):
        """
        Get the most recently completed race.
        
        Returns:
            str: Race ID of the most recent race, or None if no completed races
        """
        data = self.load_data()
        if not data:
            return None
        
        try:
            races = data['races']
            past_races = races[races['Date'] <= datetime.now()]
            
            if past_races.empty:
                logger.info("No past races found.")
                return None
            
            most_recent = past_races.sort_values(by='Date', ascending=False).iloc[0]
            return most_recent['RaceID']
        except Exception as e:
            logger.error(f"Error retrieving most recent race: {e}")
            return None
    
    def calculate_player_points_for_race(self, race_id):
        """
        Calculate fantasy points for all players for a specific race.
        
        Args:
            race_id (str): Race ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Load necessary data
            data = self.load_data(refresh=True)
            if not data:
                return False
            
            race_results = data['race_results']
            player_picks = data['player_picks']
            driver_assignments = data['driver_assignments']
            races = data['races']
            
            # Get race date
            race_info = races[races['RaceID'] == race_id]
            if race_info.empty:
                logger.error(f"Race {race_id} not found")
                return False
                
            race_date = race_info.iloc[0]['Date']
            
            # Check if this is Abu Dhabi (last race) which counts double
            is_abu_dhabi = (race_id == 'ABU')
            multiplier = 2 if is_abu_dhabi else 1
            
            # Filter for this specific race
            race_results_filtered = race_results[race_results['RaceID'] == race_id]
            race_assignments = driver_assignments[driver_assignments['RaceID'] == race_id]
            
            # Get all unique players
            players = player_picks['PlayerID'].unique()
            
            # Calculate points for each player
            player_results_data = []
            for player_id in players:
                # Get drivers picked by this player for the race date
                player_drivers = player_picks[
                    (player_picks['PlayerID'] == player_id) & 
                    (player_picks['FromDate'] <= race_date) & 
                    ((player_picks['ToDate'] >= race_date) | (player_picks['ToDate'].isna()))
                ]['DriverID'].tolist()
                
                # Initialize points and calculation details
                total_points = 0
                calculation_details = []
                
                # Process each driver picked by this player
                for driver_id in player_drivers:
                    # Check if driver was substituted for this race
                    substitution = race_assignments[race_assignments['SubstitutedForDriverID'] == driver_id]
                    
                    if not substitution.empty:
                        # Driver was substituted, use substitute's points
                        substitute_id = substitution.iloc[0]['DriverID']
                        substitute_points = race_results_filtered[race_results_filtered['DriverID'] == substitute_id]
                        
                        if not substitute_points.empty:
                            driver_points = substitute_points.iloc[0]['Points'] * multiplier
                            total_points += driver_points
                            
                            if is_abu_dhabi:
                                calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {substitute_points.iloc[0]['Points']} x2 = {driver_points}")
                            else:
                                calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {driver_points}")
                                
                            logger.info(f"Player {player_id} scored {driver_points} points from substitute driver {substitute_id} for {driver_id}")
                    else:
                        # No substitution, use driver's own points
                        driver_points = race_results_filtered[race_results_filtered['DriverID'] == driver_id]
                        
                        if not driver_points.empty:
                            points = driver_points.iloc[0]['Points'] * multiplier
                            total_points += points
                            
                            if is_abu_dhabi:
                                calculation_details.append(f"{driver_id}: {driver_points.iloc[0]['Points']} x2 = {points}")
                            else:
                                calculation_details.append(f"{driver_id}: {points}")
                                
                            logger.info(f"Player {player_id} scored {points} points from driver {driver_id}")
                
                # Add player's total points for this race
                player_results_data.append({
                    'RaceID': race_id,
                    'PlayerID': player_id,
                    'Points': total_points,
                    'CalculationDetails': ', '.join(calculation_details)
                })
            
            # Save player results
            self.save_player_results(race_id, player_results_data)
            
            logger.info(f"Successfully calculated player points for race {race_id}.")
            return True
        except Exception as e:
            logger.error(f"Error calculating player points: {e}")
            return False
    
    def backup_excel_file(self, backup_path=None):
        """
        Create a backup of the Excel file.
        
        Args:
            backup_path (str, optional): Path to save the backup
            
        Returns:
            str: Backup file path if successful, None otherwise
        """
        if not self._check_excel_access():
            return None
        
        try:
            import shutil
            
            # Generate backup filename with timestamp if not provided
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{os.path.splitext(os.path.basename(self.excel_file))[0]}_backup_{timestamp}.xlsx"
                backup_path = os.path.join(os.path.dirname(self.excel_file), backup_name)
            
            # Copy file
            shutil.copy2(self.excel_file, backup_path)
            logger.info(f"Backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
        
    def _process_race_results(self, raw_data):
        """
        Convert cumulative race results to per-race points for drivers.
        This is critical for accurate race-by-race analysis.
        
        Args:
            raw_data (Dict[str, pd.DataFrame]): Raw data with cumulative points
            
        Returns:
            pd.DataFrame: Processed race results with per-race points
        """
        # Create a copy to avoid modifying the original
        race_results = raw_data['race_results'].copy()
        
        # Get completed races sorted by date
        completed_races = raw_data['races'][raw_data['races']['Status'] == 'Completed']
        completed_races = completed_races.sort_values(by='Date')
        completed_race_ids = completed_races['RaceID'].tolist()
        
        if not completed_race_ids:
            return race_results
        
        # Store original data for reference
        original_race_results = race_results.copy()
        
        # Process each driver
        per_race_driver_results = []
        
        for driver_id in raw_data['drivers']['DriverID'].unique():
            # Extract driver results for completed races
            driver_results = original_race_results[original_race_results['DriverID'] == driver_id]
            if driver_results.empty:
                continue
            
            # Map race ID to cumulative points
            cumulative_points_map = {}
            for _, row in driver_results.iterrows():
                cumulative_points_map[row['RaceID']] = row['Points']
            
            # Calculate per-race points by comparing with previous race
            prev_points = 0
            for race_id in completed_race_ids:
                if race_id in cumulative_points_map:
                    current_points = cumulative_points_map[race_id]
                    race_points = current_points - prev_points
                    prev_points = current_points
                else:
                    race_points = 0
                    
                per_race_driver_results.append({
                    'RaceID': race_id,
                    'DriverID': driver_id,
                    'Points': race_points,
                    'CumulativePoints': prev_points
                })
        
        # Return the processed results
        if per_race_driver_results:
            return pd.DataFrame(per_race_driver_results)
        else:
            return race_results

    def _process_player_results(self, raw_data, race_results_df):
        """
        Convert cumulative player results to per-race points.
        This matches the driver points processing and ensures consistency.
        
        Args:
            raw_data (Dict[str, pd.DataFrame]): Raw data with cumulative points
            race_results_df (pd.DataFrame): Processed race results
            
        Returns:
            pd.DataFrame: Processed player results with per-race points
        """
        # Create a copy to avoid modifying the original
        player_results = raw_data['player_results'].copy()
        
        # Get completed races sorted by date
        completed_races = raw_data['races'][raw_data['races']['Status'] == 'Completed']
        completed_races = completed_races.sort_values(by='Date')
        completed_race_ids = completed_races['RaceID'].tolist()
        
        if not completed_race_ids:
            return player_results
        
        # Store original data for reference
        original_player_results = player_results.copy()
        
        # Process each player
        per_race_player_results = []
        
        for player_id in original_player_results['PlayerID'].unique():
            # Get player results
            player_history = original_player_results[original_player_results['PlayerID'] == player_id]
            if player_history.empty:
                continue
            
            # Map race ID to data
            player_data_map = {}
            for _, row in player_history.iterrows():
                player_data_map[row['RaceID']] = {
                    'Points': row['Points'],
                    'CalculationDetails': row['CalculationDetails'] if 'CalculationDetails' in row else ""
                }
            
            # Calculate per-race points
            prev_points = 0
            for race_id in completed_race_ids:
                if race_id in player_data_map:
                    current_points = player_data_map[race_id]['Points']
                    calc_details = player_data_map[race_id]['CalculationDetails']
                    race_points = current_points - prev_points
                    prev_points = current_points
                else:
                    race_points = 0
                    calc_details = ""
                    
                # Create new calculation details based on per-race points
                new_calc_details = self._regenerate_calculation_details(
                    race_id, 
                    calc_details, 
                    race_results_df
                )
                
                per_race_player_results.append({
                    'RaceID': race_id,
                    'PlayerID': player_id,
                    'Points': race_points,
                    'CumulativePoints': prev_points,
                    'CalculationDetails': new_calc_details
                })
        
        # Return the processed results
        if per_race_player_results:
            return pd.DataFrame(per_race_player_results)
        else:
            return player_results

    def calculate_player_points_for_race(self, race_id):
        """
        Calculate fantasy points for all players for a specific race,
        including substitution handling and Abu Dhabi double points.
        
        Args:
            race_id (str): Race ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._check_excel_access():
            return False
        
        try:
            # Load necessary data
            data = self.load_data(refresh=True)
            if not data:
                return False
            
            race_results = data['race_results']
            player_picks = data['player_picks']
            driver_assignments = data['driver_assignments']
            races = data['races']
            
            # Get race date
            race_info = races[races['RaceID'] == race_id]
            if race_info.empty:
                logger.error(f"Race {race_id} not found")
                return False
                
            race_date = race_info.iloc[0]['Date']
            
            # Check if this is Abu Dhabi (last race) which counts double
            is_abu_dhabi = (race_id == 'ABU')
            multiplier = 2 if is_abu_dhabi else 1
            
            # Filter for this specific race
            race_results_filtered = race_results[race_results['RaceID'] == race_id]
            race_assignments = driver_assignments[driver_assignments['RaceID'] == race_id]
            
            # Get all unique players
            players = player_picks['PlayerID'].unique()
            
            # Calculate points for each player
            player_results_data = []
            for player_id in players:
                # Get drivers picked by this player for the race date
                player_drivers = player_picks[
                    (player_picks['PlayerID'] == player_id) & 
                    (player_picks['FromDate'] <= race_date) & 
                    ((player_picks['ToDate'] >= race_date) | (player_picks['ToDate'].isna()))
                ]['DriverID'].tolist()
                
                # Initialize points and calculation details
                total_points = 0
                calculation_details = []
                
                # Process each driver picked by this player
                for driver_id in player_drivers:
                    # Check if driver was substituted for this race
                    substitution = race_assignments[race_assignments['SubstitutedForDriverID'] == driver_id]
                    
                    if not substitution.empty:
                        # Driver was substituted, use substitute's points
                        substitute_id = substitution.iloc[0]['DriverID']
                        substitute_points = race_results_filtered[race_results_filtered['DriverID'] == substitute_id]
                        
                        if not substitute_points.empty:
                            driver_points = substitute_points.iloc[0]['Points'] * multiplier
                            total_points += driver_points
                            
                            if is_abu_dhabi:
                                calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {substitute_points.iloc[0]['Points']} x2 = {driver_points}")
                            else:
                                calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {driver_points}")
                                
                            logger.info(f"Player {player_id} scored {driver_points} points from substitute driver {substitute_id} for {driver_id}")
                    else:
                        # No substitution, use driver's own points
                        driver_points = race_results_filtered[race_results_filtered['DriverID'] == driver_id]
                        
                        if not driver_points.empty:
                            points = driver_points.iloc[0]['Points'] * multiplier
                            total_points += points
                            
                            if is_abu_dhabi:
                                calculation_details.append(f"{driver_id}: {driver_points.iloc[0]['Points']} x2 = {points}")
                            else:
                                calculation_details.append(f"{driver_id}: {points}")
                                
                            logger.info(f"Player {player_id} scored {points} points from driver {driver_id}")
                
                # Add player's total points for this race
                player_results_data.append({
                    'RaceID': race_id,
                    'PlayerID': player_id,
                    'Points': total_points,
                    'CalculationDetails': ', '.join(calculation_details)
                })
            
            # Save player results
            self.save_player_results(race_id, player_results_data)
            
            logger.info(f"Successfully calculated player points for race {race_id}.")
            return True
        except Exception as e:
            logger.error(f"Error calculating player points: {e}")
            return False        
        



    def _process_substitutions_for_race(self, race_id, race_date, driver_points, player_drivers, player_id, calculation_details, is_abu_dhabi=False):
        """
        Process driver substitutions for a specific race when calculating player points.
        
        Args:
            race_id (str): Race ID
            race_date (datetime): Race date
            driver_points (dict): Dictionary mapping driver IDs to their points
            player_drivers (list): List of driver IDs picked by the player
            player_id (str): Player ID
            calculation_details (list): List to add calculation details to
            is_abu_dhabi (bool): Whether this is the Abu Dhabi GP (double points)
            
        Returns:
            float: Total points for the player after substitution processing
        """
        total_points = 0
        multiplier = 2 if is_abu_dhabi else 1
        
        # Get race assignments (substitutions)
        race_assignments = self.data_cache.get('driver_assignments', pd.DataFrame())
        race_assignments = race_assignments[race_assignments['RaceID'] == race_id]
        
        # Process each driver picked by this player
        for driver_id in player_drivers:
            # Check if driver was substituted for this race
            substitution = race_assignments[race_assignments['SubstitutedForDriverID'] == driver_id]
            
            if not substitution.empty:
                # Driver was substituted, use substitute's points
                substitute_id = substitution.iloc[0]['DriverID']
                if substitute_id in driver_points:
                    substitute_points = driver_points[substitute_id]
                    points = substitute_points * multiplier
                    total_points += points
                    
                    if is_abu_dhabi:
                        calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {substitute_points} x2 = {points}")
                    else:
                        calculation_details.append(f"{driver_id} (subbed by {substitute_id}): {points}")
                        
                    logger.info(f"Player {player_id} scored {points} points from substitute driver {substitute_id} for {driver_id}")
                else:
                    # Substitute didn't score points
                    calculation_details.append(f"{driver_id} (subbed by {substitute_id}): 0")
            else:
                # No substitution, use driver's own points
                if driver_id in driver_points:
                    driver_point_value = driver_points[driver_id]
                    points = driver_point_value * multiplier
                    total_points += points
                    
                    if is_abu_dhabi:
                        calculation_details.append(f"{driver_id}: {driver_point_value} x2 = {points}")
                    else:
                        calculation_details.append(f"{driver_id}: {points}")
                        
                    logger.info(f"Player {player_id} scored {points} points from driver {driver_id}")
                else:
                    # Driver didn't score points
                    calculation_details.append(f"{driver_id}: 0")
        
        return total_points