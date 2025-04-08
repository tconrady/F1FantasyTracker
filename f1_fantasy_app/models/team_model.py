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