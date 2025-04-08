"""
utils/image_loader.py - Image loading utilities for F1 Fantasy application
"""

import os
import logging
from PIL import Image, ImageTk

# Configure logging
logger = logging.getLogger(__name__)

class ImageLoader:
    """Image loading utility for F1 Fantasy application"""
    
    def __init__(self, images_dir="images"):
        """
        Initialize the image loader with the images directory.
        
        Args:
            images_dir (str): Path to images directory
        """
        self.images_dir = images_dir
        self.images_cache = {}  # Cache for loaded images
        self.driver_images = {}  # Map driver IDs to image filenames
        self.team_images = {}    # Map team IDs to image filenames
        self.logo_images = {}    # Map team IDs to logo filenames
        self.load_image_mappings()
    
    def load_image_mappings(self):
        """Load mappings from driver/team IDs to image filenames"""
        try:
            # Check if images directory exists
            if not os.path.exists(self.images_dir):
                logger.warning(f"Images directory '{self.images_dir}' not found. Images will not be displayed.")
                return
            
            # Map driver IDs to image filenames (based on filename patterns)
            driver_mapping = {
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
            
            # Map team IDs to car image filenames
            team_mapping = {
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
            
            # Map team IDs to logo image filenames
            logo_mapping = {
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
            
            # Store the mappings
            self.driver_images = driver_mapping
            self.team_images = team_mapping
            self.logo_images = logo_mapping
            
            logger.info(f"Image mappings loaded successfully for {len(driver_mapping)} drivers and {len(team_mapping)} teams")
        except Exception as e:
            logger.error(f"Error loading image mappings: {e}")
    
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
            try:
                # Import AVIF plugin - need to handle this import
                try:
                    from pillow_avif import AvifImagePlugin  # Make sure pillow-avif-plugin is installed
                except ImportError:
                    logger.warning("pillow-avif-plugin not found. Please install it to display AVIF images.")
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
                logger.error(f"Error processing image {filename}: {e}")
                return None
        
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
        
        logger.debug(f"No image mapping found for driver ID: {driver_id}")
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
        
        logger.debug(f"No car image mapping found for team ID: {team_id}")
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
        
        logger.debug(f"No logo mapping found for team ID: {team_id}")
        return None
    
    def create_placeholder_image(self, text, size=(60, 60), color=(200, 200, 200)):
        """
        Create a placeholder image with text.
        
        Args:
            text (str): Text to display
            size (tuple): Image size (width, height)
            color (tuple): RGB color tuple
            
        Returns:
            ImageTk.PhotoImage: Placeholder image
        """
        try:
            # Create a new image with the specified color
            img = Image.new('RGB', size, color=color)
            
            # Add text to the image if PIL's ImageDraw is available
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Try to use a default font, or fallback to the default
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except IOError:
                    font = ImageFont.load_default()
                
                # Calculate text position for center alignment
                text_width = draw.textlength(text, font=font)
                text_height = 12  # Approximation
                text_x = (size[0] - text_width) / 2
                text_y = (size[1] - text_height) / 2
                
                # Draw the text
                draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)
            except Exception as e:
                # If text drawing fails, just use the plain colored image
                logger.debug(f"Error adding text to placeholder image: {e}")
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            return photo_img
        except Exception as e:
            logger.error(f"Error creating placeholder image: {e}")
            return None