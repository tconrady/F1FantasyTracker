"""
models/player_model.py - Player-related model classes
"""

from datetime import datetime
from models.base_model import BaseModel

class Player(BaseModel):
    """Model representing a fantasy player"""
    
    def __init__(self, data=None):
        """
        Initialize a player model.
        
        Args:
            data (dict, optional): Initial player data
        """
        super().__init__(data)
    
    @property
    def id(self):
        """Get the player ID"""
        return self._data.get('PlayerID')
    
    @property
    def name(self):
        """Get the player name"""
        return self._data.get('PlayerName')
    
    def __str__(self):
        """String representation of the player"""
        return f"{self.name} ({self.id})"

class PlayerPick(BaseModel):
    """Model representing a player's driver pick"""
    
    def __init__(self, data=None):
        """
        Initialize a player pick model.
        
        Args:
            data (dict, optional): Initial player pick data
        """
        super().__init__(data)
    
    @property
    def player_id(self):
        """Get the player ID"""
        return self._data.get('PlayerID')
    
    @property
    def player_name(self):
        """Get the player name"""
        return self._data.get('PlayerName')
    
    @property
    def driver_id(self):
        """Get the driver ID"""
        return self._data.get('DriverID')
    
    @property
    def from_date(self):
        """Get the from date"""
        return self._data.get('FromDate')
    
    @property
    def to_date(self):
        """Get the to date"""
        return self._data.get('ToDate')
    
    def is_active(self, date=None):
        """
        Check if this pick is active on the given date.
        
        Args:
            date (datetime, optional): Date to check (defaults to now)
            
        Returns:
            bool: True if the pick is active on the given date
        """
        if date is None:
            date = datetime.now()
        
        # Check from date
        if self.from_date and self.from_date > date:
            return False
        
        # Check to date
        if self.to_date and self.to_date < date:
            return False
        
        return True
    
    def __str__(self):
        """String representation of the player pick"""
        status = "Active" if self.is_active() else "Inactive"
        return f"{self.player_name} ({self.player_id}) - {self.driver_id} [{status}]"

class PlayerResult(BaseModel):
    """Model representing a player's race result"""
    
    def __init__(self, data=None):
        """
        Initialize a player result model.
        
        Args:
            data (dict, optional): Initial player result data
        """
        super().__init__(data)
    
    @property
    def race_id(self):
        """Get the race ID"""
        return self._data.get('RaceID')
    
    @property
    def player_id(self):
        """Get the player ID"""
        return self._data.get('PlayerID')
    
    @property
    def points(self):
        """Get the points scored"""
        return self._data.get('Points', 0)
    
    @property
    def cumulative_points(self):
        """Get the cumulative points (if available)"""
        return self._data.get('CumulativePoints', self.points)
    
    @property
    def calculation_details(self):
        """Get the calculation details"""
        return self._data.get('CalculationDetails', "")
    
    def parse_calculation_details(self):
        """
        Parse the calculation details into a dictionary.
        
        Returns:
            dict: Dictionary mapping driver ID to points contribution
        """
        if not self.calculation_details:
            return {}
        
        driver_points = {}
        for part in self.calculation_details.split(','):
            part = part.strip()
            if ':' in part:
                driver_part, points_part = part.split(':', 1)
                driver_id = driver_part.strip().split()[0]
                
                try:
                    points = float(points_part.strip())
                except ValueError:
                    # Try to extract the number from the points part
                    import re
                    match = re.search(r'-?\d+(\.\d+)?', points_part)
                    if match:
                        points = float(match.group(0))
                    else:
                        points = 0
                
                driver_points[driver_id] = points
        
        return driver_points
    
    def __str__(self):
        """String representation of the player result"""
        return f"{self.player_id} - {self.race_id}: {self.points} points"