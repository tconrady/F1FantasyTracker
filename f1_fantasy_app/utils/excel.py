"""
utils/excel.py - Functions for Excel file operations
"""

import os
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def is_file_accessible(filepath, mode='r'):
    """
    Check if a file is accessible with the given mode.
    
    Args:
        filepath (str): Path to the file
        mode (str): Access mode to check ('r' for read, 'w' for write)
        
    Returns:
        bool: True if accessible, False otherwise
    """
    try:
        f = open(filepath, mode)
        f.close()
        return True
    except IOError:
        return False

def create_excel_if_not_exists(excel_file, sheet_names):
    """
    Create the Excel file with required sheets if it doesn't exist.
    
    Args:
        excel_file (str): Path to the Excel file
        sheet_names (dict): Dictionary of sheet names
        
    Returns:
        bool: True if successful, False otherwise
    """
    if os.path.exists(excel_file):
        logger.info(f"Excel file {excel_file} already exists.")
        return True
    
    try:
        logger.info(f"Creating new Excel file {excel_file} with required sheets.")
        
        # Create empty DataFrames for each sheet with appropriate columns
        df_races = pd.DataFrame(columns=['RaceID', 'Name', 'Date', 'Status'])
        df_drivers = pd.DataFrame(columns=['DriverID', 'Name', 'DefaultTeam', 'Credits'])
        df_teams = pd.DataFrame(columns=['TeamID', 'Name'])
        df_player_picks = pd.DataFrame(columns=['PlayerID', 'PlayerName', 'DriverID', 'FromDate', 'ToDate'])
        df_driver_assignments = pd.DataFrame(columns=['RaceID', 'DriverID', 'TeamID', 'SubstitutedForDriverID'])
        df_race_results = pd.DataFrame(columns=['RaceID', 'DriverID', 'Points'])
        df_player_results = pd.DataFrame(columns=['RaceID', 'PlayerID', 'Points', 'CalculationDetails'])
        
        # Create Excel writer and save all DataFrames to their respective sheets
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df_races.to_excel(writer, sheet_name=sheet_names['RACES'], index=False)
            df_drivers.to_excel(writer, sheet_name=sheet_names['DRIVERS'], index=False)
            df_teams.to_excel(writer, sheet_name=sheet_names['TEAMS'], index=False)
            df_player_picks.to_excel(writer, sheet_name=sheet_names['PLAYER_PICKS'], index=False)
            df_driver_assignments.to_excel(writer, sheet_name=sheet_names['DRIVER_ASSIGNMENTS'], index=False)
            df_race_results.to_excel(writer, sheet_name=sheet_names['RACE_RESULTS'], index=False)
            df_player_results.to_excel(writer, sheet_name=sheet_names['PLAYER_RESULTS'], index=False)
        
        logger.info(f"Excel file {excel_file} created successfully with all required sheets.")
        return True
        
    except Exception as e:
        logger.error(f"Error creating Excel file: {e}")
        return False

def backup_excel_file(excel_file, backup_path=None):
    """
    Create a backup of the Excel file.
    
    Args:
        excel_file (str): Path to the Excel file
        backup_path (str, optional): Path to save the backup
        
    Returns:
        str: Backup file path if successful, None otherwise
    """
    if not is_file_accessible(excel_file, 'r'):
        logger.error(f"Cannot access {excel_file} for reading")
        return None
    
    try:
        import shutil
        
        # Generate backup filename with timestamp if not provided
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.splitext(os.path.basename(excel_file))[0]}_backup_{timestamp}.xlsx"
            backup_path = os.path.join(os.path.dirname(excel_file), backup_name)
        
        # Copy file
        shutil.copy2(excel_file, backup_path)
        logger.info(f"Backup created at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

def save_dataframe_to_excel(excel_file, df, sheet_name, if_sheet_exists='replace'):
    """
    Save a DataFrame to an Excel sheet.
    
    Args:
        excel_file (str): Path to the Excel file
        df (pd.DataFrame): DataFrame to save
        sheet_name (str): Sheet name
        if_sheet_exists (str): How to handle existing sheets ('replace', 'overlay', 'new')
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not is_file_accessible(excel_file, 'r+'):
        logger.error(f"Cannot access {excel_file} for writing")
        return False
    
    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists=if_sheet_exists) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Data saved to sheet {sheet_name} in {excel_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to Excel: {e}")
        return False

def read_sheet_from_excel(excel_file, sheet_name):
    """
    Read a sheet from an Excel file.
    
    Args:
        excel_file (str): Path to the Excel file
        sheet_name (str): Sheet name
        
    Returns:
        pd.DataFrame: DataFrame containing the sheet data, or empty DataFrame if error
    """
    if not is_file_accessible(excel_file, 'r'):
        logger.error(f"Cannot access {excel_file} for reading")
        return pd.DataFrame()
    
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        logger.info(f"Read {len(df)} rows from sheet {sheet_name} in {excel_file}")
        return df
    except Exception as e:
        logger.error(f"Error reading sheet {sheet_name} from Excel: {e}")
        return pd.DataFrame()