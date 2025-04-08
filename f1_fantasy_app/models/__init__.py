"""
models/__init__.py - Initialize models package and provide a central registry
"""

from models.base_model import BaseModel
from models.driver_model import Driver, DriverResult
from models.player_model import Player, PlayerPick, PlayerResult
from models.race_model import Race, DriverAssignment
from models.team_model import Team, FantasyTeam

class ModelRegistry:
    """
    Registry for creating model instances from data.
    This centralized registry makes it easier to create the right model type
    for different kinds of data without needing to import specific model classes
    throughout the application.
    """
    
    @staticmethod
    def create_driver(data):
        """Create a Driver model from data"""
        return Driver(data)
    
    @staticmethod
    def create_driver_result(data):
        """Create a DriverResult model from data"""
        return DriverResult(data)
    
    @staticmethod
    def create_player(data):
        """Create a Player model from data"""
        return Player(data)
    
    @staticmethod
    def create_player_pick(data):
        """Create a PlayerPick model from data"""
        return PlayerPick(data)
    
    @staticmethod
    def create_player_result(data):
        """Create a PlayerResult model from data"""
        return PlayerResult(data)
    
    @staticmethod
    def create_race(data):
        """Create a Race model from data"""
        return Race(data)
    
    @staticmethod
    def create_driver_assignment(data):
        """Create a DriverAssignment model from data"""
        return DriverAssignment(data)
    
    @staticmethod
    def create_team(data):
        """Create a Team model from data"""
        return Team(data)
    
    @staticmethod
    def create_fantasy_team(player=None, drivers=None):
        """Create a FantasyTeam model"""
        return FantasyTeam(player, drivers)
    
    @staticmethod
    def create_models_from_dataframe(df, model_type):
        """
        Create a list of models from a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing data
            model_type (str): Type of model to create ('driver', 'race', etc.)
            
        Returns:
            list: List of model instances
        """
        models = []
        
        for _, row in df.iterrows():
            data = row.to_dict()
            
            if model_type == 'driver':
                models.append(ModelRegistry.create_driver(data))
            elif model_type == 'driver_result':
                models.append(ModelRegistry.create_driver_result(data))
            elif model_type == 'player':
                models.append(ModelRegistry.create_player(data))
            elif model_type == 'player_pick':
                models.append(ModelRegistry.create_player_pick(data))
            elif model_type == 'player_result':
                models.append(ModelRegistry.create_player_result(data))
            elif model_type == 'race':
                models.append(ModelRegistry.create_race(data))
            elif model_type == 'driver_assignment':
                models.append(ModelRegistry.create_driver_assignment(data))
            elif model_type == 'team':
                models.append(ModelRegistry.create_team(data))
            
        return models