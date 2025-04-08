"""
models/driver_model.py - Driver-related model classes
"""

from models.base_model import BaseModel

class Driver(BaseModel):
    """Model representing an F1 driver"""
    
    def __init__(self, data=None):
        """
        Initialize a driver model.
        
        Args:
            data (dict, optional): Initial driver data
        """
        super().__init__(data)
    
    @property
    def id(self):
        """Get the driver ID"""
        return self._data.get('DriverID')
    
    @property
    def name(self):
        """Get the driver name"""
        return self._data.get('Name')
    
    @property
    def team_id(self):
        """Get the driver's team ID"""
        return self._data.get('DefaultTeam')
    
    @property
    def credits(self):
        """Get the driver's credit value"""
        return self._data.get('Credits', 0)
    
    def is_reserve(self):
        """
        Check if this is a reserve driver.
        
        Returns:
            bool: True if this is a reserve driver (0 credits)
        """
        return self.credits == 0
    
    def __str__(self):
        """String representation of the driver"""
        return f"{self.name} ({self.id})"
    
    def format_with_credits(self):
        """
        Format driver name with ID and credits.
        
        Returns:
            str: Formatted string like "Driver Name (ID) - X credits"
        """
        return f"{self.name} ({self.id}) - {self.credits} credits"

class DriverResult(BaseModel):
    """Model representing a driver's race result"""
    
    def __init__(self, data=None):
        """
        Initialize a driver result model.
        
        Args:
            data (dict, optional): Initial driver result data
        """
        super().__init__(data)
    
    @property
    def race_id(self):
        """Get the race ID"""
        return self._data.get('RaceID')
    
    @property
    def driver_id(self):
        """Get the driver ID"""
        return self._data.get('DriverID')
    
    @property
    def points(self):
        """Get the points scored"""
        return self._data.get('Points', 0)
    
    @property
    def cumulative_points(self):
        """Get the cumulative points (if available)"""
        return self._data.get('CumulativePoints', self.points)
    
    def __str__(self):
        """String representation of the driver result"""
        return f"{self.driver_id} - {self.race_id}: {self.points} points"