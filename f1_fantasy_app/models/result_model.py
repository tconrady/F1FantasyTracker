"""
models/result_model.py - Result-related model classes
"""

from models.base_model import BaseModel

class Result(BaseModel):
    """Base class for all result models"""
    
    def __init__(self, data=None):
        """
        Initialize a result model.
        
        Args:
            data (dict, optional): Initial result data
        """
        super().__init__(data)
    
    @property
    def race_id(self):
        """Get the race ID"""
        return self._data.get('RaceID')
    
    @property
    def points(self):
        """Get the points scored"""
        return self._data.get('Points', 0)

class RaceResult(Result):
    """Model representing overall race results"""
    
    def __init__(self, data=None):
        """Initialize a race result model."""
        super().__init__(data)
    
    @property
    def standings(self):
        """Get the standings after this race"""
        return self._data.get('Standings', [])
    
    @property
    def completed(self):
        """Check if the race is completed"""
        return self._data.get('Completed', False)
    
    def __str__(self):
        """String representation of the race result"""
        return f"Race Result: {self.race_id} - Completed: {self.completed}"

class StandingsResult(BaseModel):
    """Model representing the current standings"""
    
    def __init__(self, data=None):
        """Initialize a standings result model."""
        super().__init__(data)
    
    @property
    def standings(self):
        """Get the standings data"""
        return self._data.get('Standings', [])
    
    @property
    def last_updated(self):
        """Get the last updated date"""
        return self._data.get('LastUpdated')
    
    @property
    def last_race_id(self):
        """Get the ID of the last race included in these standings"""
        return self._data.get('LastRaceID')
    
    def __str__(self):
        """String representation of the standings result"""
        return f"Standings (Last Race: {self.last_race_id}, Updated: {self.last_updated})"