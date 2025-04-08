"""
models/race_model.py - Race-related model classes
"""

from models.base_model import BaseModel

class Race(BaseModel):
    """Model representing an F1 race"""
    
    def __init__(self, data=None):
        """
        Initialize a race model.
        
        Args:
            data (dict, optional): Initial race data
        """
        super().__init__(data)
    
    @property
    def id(self):
        """Get the race ID"""
        return self._data.get('RaceID')
    
    @property
    def name(self):
        """Get the race name"""
        return self._data.get('Name')
    
    @property
    def date(self):
        """Get the race date"""
        return self._data.get('Date')
    
    @property
    def status(self):
        """Get the race status"""
        return self._data.get('Status', 'Upcoming')
    
    @property
    def is_completed(self):
        """Check if the race is completed"""
        return self.status == 'Completed'
    
    @property
    def is_abu_dhabi(self):
        """Check if this is the Abu Dhabi Grand Prix (last race, double points)"""
        return self.id == 'ABU'
    
    def formatted_date(self, format_str='%Y-%m-%d'):
        """
        Get the formatted race date.
        
        Args:
            format_str (str): Date format string
            
        Returns:
            str: Formatted date
        """
        if self.date:
            return self.date.strftime(format_str)
        return ""
    
    def __str__(self):
        """String representation of the race"""
        date_str = self.formatted_date() if self.date else "Unknown date"
        return f"{self.name} ({self.id}) - {date_str} [{self.status}]"

class DriverAssignment(BaseModel):
    """Model representing a driver substitution/assignment for a race"""
    
    def __init__(self, data=None):
        """
        Initialize a driver assignment model.
        
        Args:
            data (dict, optional): Initial driver assignment data
        """
        super().__init__(data)
    
    @property
    def race_id(self):
        """Get the race ID"""
        return self._data.get('RaceID')
    
    @property
    def driver_id(self):
        """Get the substitute driver ID"""
        return self._data.get('DriverID')
    
    @property
    def team_id(self):
        """Get the team ID"""
        return self._data.get('TeamID')
    
    @property
    def substituted_for_driver_id(self):
        """Get the driver ID being substituted"""
        return self._data.get('SubstitutedForDriverID')
    
    def __str__(self):
        """String representation of the driver assignment"""
        return f"Race {self.race_id}: {self.driver_id} replacing {self.substituted_for_driver_id} at {self.team_id}"