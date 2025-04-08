"""
models/base_model.py - Base model class for all domain models
"""

class BaseModel:
    """Base class for all domain models in the application"""
    
    def __init__(self, data=None):
        """
        Initialize the base model.
        
        Args:
            data (dict, optional): Initial data for the model
        """
        self._data = data or {}
    
    def __getattr__(self, name):
        """
        Get an attribute from the model data.
        
        Args:
            name (str): Attribute name
            
        Returns:
            Any: Attribute value
            
        Raises:
            AttributeError: If the attribute is not found
        """
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """
        Set an attribute in the model data.
        
        Args:
            name (str): Attribute name
            value (Any): Attribute value
        """
        if name.startswith('_'):
            # Private attribute
            super().__setattr__(name, value)
        else:
            # Public attribute - store in data dict
            self._data[name] = value
    
    def get_data(self):
        """
        Get all data from the model.
        
        Returns:
            dict: Model data
        """
        return self._data.copy()
    
    def update(self, data):
        """
        Update model data.
        
        Args:
            data (dict): New data to update the model with
            
        Returns:
            BaseModel: Self for chaining
        """
        self._data.update(data)
        return self
    
    def to_dict(self):
        """
        Convert model to dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return self._data.copy()