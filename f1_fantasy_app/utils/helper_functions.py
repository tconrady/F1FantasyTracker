"""
utils/helper_functions.py - Helper functions for the F1 Fantasy Tracker
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def add_new_driver(data_manager, driver_id, driver_name, team_id, credits=0, is_reserve=False):
    """
    Add a new driver to the system.
    
    Args:
        data_manager: Data manager instance
        driver_id (str): Driver ID (e.g., 'BEA' for Bearman)
        driver_name (str): Full driver name
        team_id (str): Team ID
        credits (int): Credit value (default 0 for reserve drivers)
        is_reserve (bool): Whether this is a reserve driver
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load current drivers
        data = data_manager.load_data()
        if not data:
            return False
            
        drivers_df = data['drivers']
        
        # Check if driver already exists
        if driver_id in drivers_df['DriverID'].values:
            logger.warning(f"Driver with ID '{driver_id}' already exists.")
            return False
        
        # Create new driver data
        new_driver = {
            'DriverID': driver_id,
            'Name': driver_name,
            'DefaultTeam': team_id,
            'Credits': 0 if is_reserve else credits
        }
        
        # Add to dataframe
        drivers_df = pd.concat([drivers_df, pd.DataFrame([new_driver])], ignore_index=True)
        
        # Save back to Excel
        with pd.ExcelWriter(data_manager.excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            drivers_df.to_excel(writer, sheet_name=data_manager.sheet_names['DRIVERS'], index=False)
        
        logger.info(f"Added new driver: {driver_name} ({driver_id}) with default team {team_id}.")
        
        # Invalidate cache to ensure fresh data is loaded next time
        data_manager.is_cache_valid = False
        
        return True
    except Exception as e:
        logger.error(f"Error adding new driver: {e}")
        return False

def validate_team_composition(driver_ids, data_manager, max_credits=5):
    """
    Validate a team composition based on driver IDs.
    
    Args:
        driver_ids (list): List of driver IDs
        data_manager: Data manager instance
        max_credits (int): Maximum allowed credits
        
    Returns:
        tuple: (is_valid, message, total_credits)
    """
    try:
        # Load data
        data = data_manager.load_data()
        if not data:
            return False, "Could not load driver data", 0
            
        drivers_df = data['drivers']
        
        # Check if we have exactly 2 drivers
        if len(driver_ids) != 2:
            return False, "A team must have exactly 2 drivers", 0
        
        # Check for duplicates
        if len(set(driver_ids)) != len(driver_ids):
            return False, "A team cannot contain the same driver twice", 0
        
        # Calculate total credits
        total_credits = 0
        driver_details = []
        
        for driver_id in driver_ids:
            driver = drivers_df[drivers_df['DriverID'] == driver_id]
            if driver.empty:
                return False, f"Driver '{driver_id}' not found", 0
                
            driver_credits = driver['Credits'].iloc[0]
            total_credits += driver_credits
            
            driver_details.append(f"{driver['Name'].iloc[0]} ({driver_id}): {driver_credits} credits")
        
        # Check credit limit
        if total_credits > max_credits:
            return False, f"Team exceeds credit limit: {total_credits}/{max_credits} credits", total_credits
        
        # Valid team
        return True, f"Valid team: {' + '.join(driver_details)} = {total_credits}/{max_credits} credits", total_credits
    except Exception as e:
        logger.error(f"Error validating team composition: {e}")
        return False, f"Error validating team: {e}", 0

def find_available_teams(data_manager, max_credits=5):
    """
    Find all valid team combinations available within the credit limit.
    
    Args:
        data_manager: Data manager instance
        max_credits (int): Maximum allowed credits
        
    Returns:
        list: List of dictionaries with valid team combinations and their details
    """
    try:
        # Load data
        data = data_manager.load_data()
        if not data:
            return []
            
        drivers_df = data['drivers']
        
        # Filter out reserve drivers (0 credits)
        active_drivers = drivers_df[drivers_df['Credits'] > 0]
        
        # Create all possible driver pairs
        valid_teams = []
        
        for i, row1 in active_drivers.iterrows():
            for j, row2 in active_drivers.iloc[i+1:].iterrows():
                # Skip if same driver (should not happen, but just in case)
                if row1['DriverID'] == row2['DriverID']:
                    continue
                
                # Calculate total credits
                total_credits = row1['Credits'] + row2['Credits']
                
                # Check if within credit limit
                if total_credits <= max_credits:
                    valid_teams.append({
                        'DriverIDs': [row1['DriverID'], row2['DriverID']],
                        'DriverNames': [f"{row1['Name']} ({row1['DriverID']})", f"{row2['Name']} ({row2['DriverID']})"],
                        'Credits': total_credits
                    })
        
        # Sort by credits (highest first)
        valid_teams.sort(key=lambda x: x['Credits'], reverse=True)
        
        return valid_teams
    except Exception as e:
        logger.error(f"Error finding available teams: {e}")
        return []