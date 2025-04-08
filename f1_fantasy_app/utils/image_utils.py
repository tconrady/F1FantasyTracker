"""
utils/image_utils.py - Utilities for loading and managing images
"""

import os
import logging
import tkinter as tk
from PIL import Image, ImageTk

# Try to import AVIF plugin
try:
    from pillow_avif import AvifImagePlugin
except ImportError:
    logging.warning("pillow-avif-plugin not found. Please install it to display AVIF images.")

logger = logging.getLogger(__name__)

class ImageManager:
    """
    Utility class for loading and caching images for the F1 Fantasy application.
    Handles driver portraits, team cars, and team logos stored as AVIF files.
    """
    
    def __init__(self, images_dir="images"):
        """
        Initialize the image manager.
        
        Args:
            images_dir (str): Path to images directory
        """
        self.images_dir = images_dir
        self.images_cache = {}  # Cache for loaded images
        
        # Create mappings from IDs to filenames
        self.driver_images = self._create_driver_mapping()
        self.team_images = self._create_team_mapping()
        self.logo_images = self._create_logo_mapping()
        
        # Ensure image directory exists
        if not os.path.exists(self.images_dir):
            logger.warning(f"Images directory '{self.images_dir}' not found. Images will not be displayed.")
    
    def _create_driver_mapping(self):
        """Create mapping from driver IDs to image filenames"""
        return {
            'ALB': 'alealb01.avif',
            'ANT': 'andant01.avif',
            'SAI': 'carsai01.avif',
            'LEC': 'chalec01.avif',
            'OCO': 'estoco01.avif',
            'ALO': 'feralo01.avif',
            'BOR': 'gabbor01.avif',
            'RUS': 'georus01.avif',
            'HAD': 'isahad01.avif',
            'DOO': 'jacdoo01.avif',
            'NOR': 'lannor01.avif',
            'STR': 'lanstr01.avif',
            'HAM': 'lewham01.avif',
            'LAW': 'lialaw01.avif',
            'VER': 'maxver01.avif',
            'HUL': 'nichul01.avif',
            'BEA': 'olibea01.avif',
            'PIA': 'oscpia01.avif',
            'GAS': 'piegas01.avif',
            'TSU': 'yuktsu01.avif'
        }
    
    def _create_team_mapping(self):
        """Create mapping from team IDs to car image filenames"""
        return {
            'ALP': 'alpine.avif',
            'AST': 'aston-martin.avif',
            'FER': 'ferrari.avif',
            'HAS': 'haas.avif',
            'SAU': 'kick-sauber.avif',
            'MCL': 'mclaren.avif',
            'MER': 'mercedes.avif',
            'RBT': 'racing-bulls.avif',
            'RBR': 'red-bull-racing.avif',
            'WIL': 'williams.avif'
        }
    
    def _create_logo_mapping(self):
        """Create mapping from team IDs to logo image filenames"""
        return {
            'ALP': 'alpine-logo.avif',
            'AST': 'aston-martin-logo.avif',
            'FER': 'ferrari-logo.avif',
            'HAS': 'haas-logo.avif',
            'SAU': 'kick-sauber-logo.avif',
            'MCL': 'mclaren-logo.avif',
            'MER': 'mercedes-logo.avif',
            'RBT': 'racing-bulls-logo.avif',
            'RBR': 'red-bull-racing-logo.avif',
            'WIL': 'williams-logo.avif'
        }
    
    def load_avif_image(self, filename, size=None):
        """
        Load an AVIF image and convert to PhotoImage for tkinter.
        
        Args:
            filename (str): Image filename
            size (tuple, optional): Size to resize the image to (width, height)
            
        Returns:
            ImageTk.PhotoImage: Tkinter-compatible image or None if failed
        """
        try:
            # Check if image is already cached
            cache_key = f"{filename}_{size}"
            if cache_key in self.images_cache:
                return self.images_cache[cache_key]
            
            # Construct full path
            path = os.path.join(self.images_dir, filename)
            
            # Check if file exists
            if not os.path.exists(path):
                logger.warning(f"Image file not found: {path}")
                return None
            
            # Try to load the image using Pillow
            if 'AvifImagePlugin' not in globals():
                logger.warning("AVIF plugin not available. Cannot load image.")
                return None
            
            img = Image.open(path)
            
            # Resize if size is specified
            if size:
                img = img.resize(size, Image.LANCZOS)
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            
            # Cache the image
            self.images_cache[cache_key] = photo_img
            
            return photo_img
        
        except Exception as e:
            logger.error(f"Error loading image {filename}: {e}")
            return None
    
    def get_driver_image(self, driver_id, size=None):
        """
        Get a driver's image.
        
        Args:
            driver_id (str): Driver ID
            size (tuple, optional): Size to resize the image to (width, height)
            
        Returns:
            ImageTk.PhotoImage: Driver image or None if not found
        """
        if driver_id in self.driver_images:
            return self.load_avif_image(self.driver_images[driver_id], size)
        return None
    
    def get_team_image(self, team_id, size=None):
        """
        Get a team's car image.
        
        Args:
            team_id (str): Team ID
            size (tuple, optional): Size to resize the image to (width, height)
            
        Returns:
            ImageTk.PhotoImage: Team image or None if not found
        """
        if team_id in self.team_images:
            return self.load_avif_image(self.team_images[team_id], size)
        return None
    
    def get_team_logo(self, team_id, size=None):
        """
        Get a team's logo.
        
        Args:
            team_id (str): Team ID
            size (tuple, optional): Size to resize the image to (width, height)
            
        Returns:
            ImageTk.PhotoImage: Team logo or None if not found
        """
        if team_id in self.logo_images:
            return self.load_avif_image(self.logo_images[team_id], size)
        return None
    
    def create_placeholder_image(self, text, size=(60, 60), bg_color=(200, 200, 200)):
        """
        Create a placeholder image with text when actual image is not available.
        
        Args:
            text (str): Text to display on the placeholder
            size (tuple): Size of the placeholder image
            bg_color (tuple): Background color as RGB tuple
            
        Returns:
            ImageTk.PhotoImage: Placeholder image
        """
        try:
            # Create a new image with a colored background
            img = Image.new('RGB', size, color=bg_color)
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            return photo_img
            
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
            return None