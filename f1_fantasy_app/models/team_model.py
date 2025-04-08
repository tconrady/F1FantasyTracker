"""
models/team_model.py - Team-related model classes
"""

from models.base_model import BaseModel

class Team(BaseModel):
    """Model representing an F1 team"""
    
    def __init__(self, data=None):
        """
        Initialize a team model.
        
        Args:
            data (dict, optional): Initial team data
        """
        super().__init__(data)
    
    @property
    def id(self):
        """Get the team ID"""
        return self._data.get('TeamID')
    
    @property
    def name(self):
        """Get the team name"""
        return self._data.get('Name')
    
    def __str__(self):
        """String representation of the team"""
        return f"{self.name} ({self.id})"

class FantasyTeam(BaseModel):
    """Model representing a player's fantasy team (combination of drivers)"""
    
    def __init__(self, player=None, drivers=None):
        """
        Initialize a fantasy team model.
        
        Args:
            player (Player, optional): Player who owns this team
            drivers (list, optional): List of Driver objects in this team
        """
        super().__init__()
        self._player = player
        self._drivers = drivers or []
    
    @property
    def player(self):
        """Get the player who owns this team"""
        return self._player
    
    @player.setter
    def player(self, value):
        """Set the player who owns this team"""
        self._player = value
    
    @property
    def drivers(self):
        """Get the drivers in this team"""
        return self._drivers.copy()
    
    def add_driver(self, driver):
        """
        Add a driver to the team.
        
        Args:
            driver (Driver): Driver to add
            
        Returns:
            bool: True if added successfully, False if team is full
        """
        if len(self._drivers) >= 2:
            return False
        
        self._drivers.append(driver)
        return True
    
    def remove_driver(self, driver_id):
        """
        Remove a driver from the team.
        
        Args:
            driver_id (str): ID of the driver to remove
            
        Returns:
            bool: True if removed successfully, False if driver not found
        """
        for i, driver in enumerate(self._drivers):
            if driver.id == driver_id:
                self._drivers.pop(i)
                return True
        return False
    
    def replace_driver(self, old_driver_id, new_driver):
        """
        Replace a driver in the team.
        
        Args:
            old_driver_id (str): ID of the driver to replace
            new_driver (Driver): New driver
            
        Returns:
            bool: True if replaced successfully, False if old driver not found
        """
        if self.remove_driver(old_driver_id):
            self.add_driver(new_driver)
            return True
        return False
    
    @property
    def total_credits(self):
        """Get the total credits used by this team"""
        return sum(driver.credits for driver in self._drivers)
    
    def is_valid(self):
        """
        Check if this team is valid.
        
        Returns:
            bool: True if the team is valid (has 2 drivers and within credit limit)
        """
        return len(self._drivers) == 2 and self.total_credits <= 5
    
    def __str__(self):
        """String representation of the fantasy team"""
        if not self._drivers:
            return "Empty team"
        
        driver_str = " + ".join(str(driver) for driver in self._drivers)
        player_str = f" ({self.player})" if self.player else ""
        return f"{driver_str}{player_str} - {self.total_credits} credits"

    def validate_team(self, drivers_data):
        """
        Validate a fantasy team composition.
        
        Args:
            drivers_data (list): List of Driver objects or driver data dictionaries
            
        Returns:
            tuple: (is_valid, message) where is_valid is a boolean and message explains any issues
        """
        # Check if we have exactly 2 drivers for standard fantasy format
        if len(drivers_data) != 2:
            return False, "A valid team must have exactly 2 drivers."
        
        # Get driver IDs
        driver_ids = []
        for driver in drivers_data:
            if isinstance(driver, dict):
                driver_id = driver.get('DriverID')
            else:
                driver_id = driver.id
            driver_ids.append(driver_id)
        
        # Check for duplicates
        if len(set(driver_ids)) != len(driver_ids):
            return False, "A team cannot contain the same driver twice."
        
        # Calculate total credit cost
        total_credits = 0
        for driver in drivers_data:
            if isinstance(driver, dict):
                credits = driver.get('Credits', 0)
            else:
                credits = driver.credits
            total_credits += credits
        
        # Check credit limit (5 is the standard limit for F1 Fantasy)
        if total_credits > 5:
            return False, f"Team exceeds the credit limit: {total_credits}/5 credits."
        
        # All validation passed
        return True, "Valid team."

    def find_available_teams(drivers_data, max_credits=5):
        """
        Find all valid team combinations within the credit limit.
        
        Args:
            drivers_data (list): List of Driver objects or driver data dictionaries
            max_credits (int): Maximum allowed credits
            
        Returns:
            list: List of valid team combinations as dicts with driver pairs and credits
        """
        valid_teams = []
        
        # Create all possible driver pairs and check if they're valid
        for i, driver1 in enumerate(drivers_data):
            for j, driver2 in enumerate(drivers_data[i+1:], i+1):
                # Get driver IDs and credits
                if isinstance(driver1, dict):
                    driver1_id = driver1.get('DriverID')
                    driver1_name = driver1.get('Name')
                    driver1_credits = driver1.get('Credits', 0)
                else:
                    driver1_id = driver1.id
                    driver1_name = driver1.name
                    driver1_credits = driver1.credits
                    
                if isinstance(driver2, dict):
                    driver2_id = driver2.get('DriverID')
                    driver2_name = driver2.get('Name')
                    driver2_credits = driver2.get('Credits', 0)
                else:
                    driver2_id = driver2.id
                    driver2_name = driver2.name
                    driver2_credits = driver2.credits
                
                # Calculate total credits
                total_credits = driver1_credits + driver2_credits
                
                # Check if within credit limit
                if total_credits <= max_credits:
                    valid_teams.append({
                        'DriverIDs': [driver1_id, driver2_id],
                        'DriverNames': [f"{driver1_name} ({driver1_id})", f"{driver2_name} ({driver2_id})"],
                        'Credits': total_credits
                    })
        
        # Sort by credits (highest first)
        valid_teams.sort(key=lambda x: x['Credits'], reverse=True)
        
        return valid_teams    