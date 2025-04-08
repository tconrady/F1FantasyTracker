"""
f1_fantasy_app.py - Main application entry point for F1 Fantasy Tracker
"""

import tkinter as tk
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import MVC components
from models.data_manager import F1DataManager
from controllers.main_controller import MainController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('f1_fantasy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Set up the Excel file path
        excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'F1_Fantasy_2025.xlsx')
        
        # Create the root Tk instance
        root = tk.Tk()
        
        # Set application icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'f1_icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        
        # Create main controller
        controller = MainController(root, excel_file)
        
        # Run the application
        controller.run()
    except Exception as e:
        logger.critical(f"Unhandled exception in main application: {e}", exc_info=True)
        if 'root' in locals():
            tk.messagebox.showerror("Critical Error", f"An unhandled error occurred: {e}\n\nSee log file for details.")

if __name__ == "__main__":
    main()