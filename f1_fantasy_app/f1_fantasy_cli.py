"""
f1_fantasy_cli.py - Command-line interface for F1 Fantasy Tracker
"""

import argparse
import logging
import sys
from datetime import datetime

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

# Import application components
from models.data_manager import F1DataManager

def init_excel(args):
    """Initialize the Excel file with default data"""
    data_manager = F1DataManager(args.file)
    if data_manager.create_excel_if_not_exists():
        if data_manager.initialize_season_data():
            print("Excel file initialized successfully with 2025 season data.")
        else:
            print("Excel file created but failed to initialize season data.")
    else:
        print("Failed to create Excel file.")

def list_races(args):
    """List all races in the season"""
    data_manager = F1DataManager(args.file)
    data = data_manager.load_data()
    
    if not data or 'races' not in data:
        print("No race data found.")
        return
    
    races = data['races'].sort_values(by='Date')
    
    print("\n===== F1 Race Calendar =====")
    print(f"{'RaceID':<6} {'Name':<30} {'Date':<12} {'Status':<10}")
    print("-" * 60)
    
    for _, race in races.iterrows():
        date_str = race['Date'].strftime('%Y-%m-%d') if not pd.isna(race['Date']) else "N/A"
        print(f"{race['RaceID']:<6} {race['Name']:<30} {date_str:<12} {race['Status']:<10}")

def list_players(args):
    """List all players and their current picks"""
    data_manager = F1DataManager(args.file)
    data = data_manager.load_data()
    
    if not data:
        print("No data found.")
        return
    
    # Get only current picks (ToDate is null)
    current_picks = data['player_picks'][data['player_picks']['ToDate'].isna()]
    
    # Group by player
    players = current_picks['PlayerID'].unique()
    
    print("\n===== Fantasy Players and Their Current Picks =====")
    
    for player_id in players:
        player_name = current_picks[current_picks['PlayerID'] == player_id]['PlayerName'].iloc[0]
        print(f"\n{player_name} ({player_id}):")
        
        player_drivers = current_picks[current_picks['PlayerID'] == player_id]
        for _, pick in player_drivers.iterrows():
            driver_id = pick['DriverID']
            driver = data['drivers'][data['drivers']['DriverID'] == driver_id]
            driver_name = driver['Name'].iloc[0] if not driver.empty else driver_id
            print(f"  - {driver_name} ({driver_id}) since {pick['FromDate'].strftime('%Y-%m-%d')}")

def update_race(args):
    """Update results for a specific race"""
    data_manager = F1DataManager(args.file)
    
    if args.race_id:
        print(f"Updating results for race {args.race_id}...")
        # For manual update, we'd just calculate points based on existing data
        if data_manager.calculate_player_points_for_race(args.race_id):
            print(f"Results for race {args.race_id} updated successfully.")
        else:
            print(f"Failed to update results for race {args.race_id}.")
    else:
        print("No race ID specified.")

def show_standings(args):
    """Show current player standings"""
    data_manager = F1DataManager(args.file)
    data = data_manager.load_data()
    
    if not data:
        print("No data found.")
        return
    
    # Get completed races to calculate standings
    completed_races = data['races'][data['races']['Status'] == 'Completed']['RaceID'].tolist()
    
    if not completed_races:
        print("No completed races found.")
        return
    
    # Calculate total points for each player
    player_total_points = {}
    player_names = {}
    
    for player_id in data['player_results']['PlayerID'].unique():
        player_results = data['player_results'][data['player_results']['PlayerID'] == player_id]
        
        # Sum points across all races
        total_points = player_results['Points'].sum()
        player_total_points[player_id] = total_points
        
        # Get player name
        player_picks = data['player_picks'][data['player_picks']['PlayerID'] == player_id]
        if not player_picks.empty:
            player_names[player_id] = player_picks['PlayerName'].iloc[0]
        else:
            player_names[player_id] = f"Player {player_id}"
    
    # Sort by total points (descending)
    sorted_players = sorted(player_total_points.items(), key=lambda x: x[1], reverse=True)
    
    print("\n===== Current Player Standings =====")
    print(f"{'Position':<10} {'Player':<20} {'Points':<10}")
    print("-" * 40)
    
    for i, (player_id, points) in enumerate(sorted_players, 1):
        player_name = player_names.get(player_id, f"Player {player_id}")
        print(f"{i:<10} {player_name:<20} {points:<10.1f}")

def main():
    parser = argparse.ArgumentParser(description='F1 Fantasy Tracker CLI')
    parser.add_argument('--file', default='F1_Fantasy_2025.xlsx', help='Excel file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize Excel file with default data')
    init_parser.set_defaults(func=init_excel)
    
    # List races command
    races_parser = subparsers.add_parser('races', help='List all races')
    races_parser.set_defaults(func=list_races)
    
    # List players command
    players_parser = subparsers.add_parser('players', help='List all players and their picks')
    players_parser.set_defaults(func=list_players)
    
    # Update race command
    update_parser = subparsers.add_parser('update', help='Update race results')
    update_parser.add_argument('race_id', help='Race ID to update (e.g., "AUS")')
    update_parser.set_defaults(func=update_race)
    
    # Show standings command
    standings_parser = subparsers.add_parser('standings', help='Show current player standings')
    standings_parser.set_defaults(func=show_standings)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    import pandas as pd  # Import here to avoid circular import issues
    main()