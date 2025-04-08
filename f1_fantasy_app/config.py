"""
config.py - Application configuration settings
"""

import os
import json
import logging
from pathlib import Path

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

class Config:
    """Application configuration settings"""
    
    # Default configuration
    _defaults = {
        "excel_file": "F1_Fantasy_2025.xlsx",
        "backup_dir": "backups",
        "images_dir": "images",
        "sheet_names": {
            "RACES": "Races",
            "DRIVERS": "Drivers",
            "TEAMS": "Teams",
            "PLAYER_PICKS": "PlayerPicks",
            "DRIVER_ASSIGNMENTS": "DriverAssignments",
            "RACE_RESULTS": "RaceResults",
            "PLAYER_RESULTS": "PlayerResults"
        },
        "ui": {
            "theme": "default",
            "window_size": "1200x800",
            "show_images": True
        },
        "fantasy": {
            "max_credits": 5,
            "team_size": 2,
            "abu_dhabi_multiplier": 2
        }
    }
    
    # Instance variables
    _instance = None
    _config = None
    _config_file = "f1_fantasy_config.json"
    
    def __new__(cls):
        """Singleton pattern - ensure only one Config instance exists"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            # Try to load from config file
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Configuration loaded from {self._config_file}")
            else:
                # Use defaults
                self._config = self._defaults.copy()
                logger.info("Using default configuration")
                
                # Save defaults to file
                self.save()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config = self._defaults.copy()
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
            logger.info(f"Configuration saved to {self._config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key (can use dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        if '.' in key:
            # Nested key
            parts = key.split('.')
            value = self._config
            for part in parts:
                if part not in value:
                    return default
                value = value[part]
            return value
        
        # Top-level key
        return self._config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key (can use dot notation for nested keys)
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if '.' in key:
                # Nested key
                parts = key.split('.')
                config = self._config
                for part in parts[:-1]:
                    if part not in config:
                        config[part] = {}
                    config = config[part]
                config[parts[-1]] = value
            else:
                # Top-level key
                self._config[key] = value
            
            return True
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
            return False
    
    def get_excel_path(self):
        """
        Get the full path to the Excel file.
        
        Returns:
            str: Full path to the Excel file
        """
        excel_file = self.get('excel_file')
        if os.path.isabs(excel_file):
            return excel_file
        
        # Relative path - resolve against application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, excel_file)
    
    def get_backup_dir(self):
        """
        Get the full path to the backup directory.
        
        Returns:
            str: Full path to the backup directory
        """
        backup_dir = self.get('backup_dir')
        if os.path.isabs(backup_dir):
            return backup_dir
        
        # Relative path - resolve against application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, backup_dir)
    
    def get_images_dir(self):
        """
        Get the full path to the images directory.
        
        Returns:
            str: Full path to the images directory
        """
        images_dir = self.get('images_dir')
        if os.path.isabs(images_dir):
            return images_dir
        
        # Relative path - resolve against application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, images_dir)
    
    def get_sheet_name(self, key):
        """
        Get the Excel sheet name for a specific key.
        
        Args:
            key (str): Sheet key (e.g., 'RACES', 'DRIVERS')
            
        Returns:
            str: Sheet name
        """
        return self.get(f'sheet_names.{key}')
    
    def get_all_sheet_names(self):
        """
        Get all Excel sheet names.
        
        Returns:
            dict: Dictionary mapping sheet keys to sheet names
        """
        return self.get('sheet_names')
    
    def get_theme(self):
        """
        Get the UI theme.
        
        Returns:
            str: Theme name
        """
        return self.get('ui.theme')
    
    def get_window_size(self):
        """
        Get the initial window size.
        
        Returns:
            str: Window size string (e.g., '1200x800')
        """
        return self.get('ui.window_size')
    
    def get_show_images(self):
        """
        Check if images should be shown.
        
        Returns:
            bool: True if images should be shown
        """
        return self.get('ui.show_images')
    
    def get_max_credits(self):
        """
        Get the maximum credits allowed for a team.
        
        Returns:
            int: Maximum credits
        """
        return self.get('fantasy.max_credits')
    
    def get_team_size(self):
        """
        Get the number of drivers per team.
        
        Returns:
            int: Team size
        """
        return self.get('fantasy.team_size')
    
    def get_abu_dhabi_multiplier(self):
        """
        Get the point multiplier for Abu Dhabi.
        
        Returns:
            int: Abu Dhabi multiplier
        """
        return self.get('fantasy.abu_dhabi_multiplier')

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
            # Try opening the file in the given mode
            f = open(filepath, mode)
            f.close()
            return True
        except IOError:
            return False

    def create_backup(excel_file, backup_dir=None):
        """
        Create a backup of an Excel file.
        
        Args:
            excel_file (str): Path to the Excel file
            backup_dir (str, optional): Backup directory
            
        Returns:
            str: Path to the backup file or None if failed
        """
        try:
            # Check if the file exists and is accessible
            if not is_file_accessible(excel_file, 'r'):
                logger.error(f"Cannot access {excel_file} for backup")
                return None
            
            # Create backup directory if it doesn't exist
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                logger.info(f"Created backup directory: {backup_dir}")
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(excel_file)
            backup_name = f"{os.path.splitext(filename)[0]}_backup_{timestamp}.xlsx"
            
            if backup_dir:
                backup_path = os.path.join(backup_dir, backup_name)
            else:
                backup_path = os.path.join(os.path.dirname(excel_file), backup_name)
            
            # Copy file
            import shutil
            shutil.copy2(excel_file, backup_path)
            logger.info(f"Backup created at {backup_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def safe_save_dataframe(df, excel_file, sheet_name, if_sheet_exists='replace'):
        """
        Safely save a DataFrame to an Excel sheet.
        
        Args:
            df (pd.DataFrame): DataFrame to save
            excel_file (str): Path to Excel file
            sheet_name (str): Sheet name to save to
            if_sheet_exists (str): How to handle existing sheets
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a backup before modifying
            create_backup(excel_file)
            
            # Save the DataFrame
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists=if_sheet_exists) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"DataFrame saved to sheet {sheet_name} in {excel_file}")
            return True
            
        except PermissionError:
            logger.error(f"Permission denied when saving to {excel_file}. The file may be open in Excel.")
            return False
        except Exception as e:
            logger.error(f"Error saving DataFrame to Excel: {e}")
            return False

    def safe_read_excel(excel_file, sheet_name=None, **kwargs):
        """
        Safely read an Excel file or sheet.
        
        Args:
            excel_file (str): Path to Excel file
            sheet_name (str, optional): Sheet name to read
            **kwargs: Additional arguments for pd.read_excel
            
        Returns:
            pd.DataFrame or dict: DataFrame(s) read from Excel
        """
        try:
            if not is_file_accessible(excel_file, 'r'):
                logger.error(f"Cannot access {excel_file} for reading")
                return None
            
            return pd.read_excel(excel_file, sheet_name=sheet_name, **kwargs)
            
        except Exception as e:
            logger.error(f"Error reading Excel file {excel_file}: {e}")
            return None