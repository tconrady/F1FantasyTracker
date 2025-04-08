"""
f1_fantasy_app.py - Main entry point for the F1 Fantasy Tracker application
"""

import tkinter as tk
import os
import sys
import logging
from datetime import datetime

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

# Import application components
from models.data_manager import F1DataManager
from controllers.main_controller import MainController

def main():
    """Main entry point for the application"""
    try:
        # Set up the Excel file path
        excel_file = 'F1_Fantasy_2025.xlsx'
        
        # Create the root Tk instance
        root = tk.Tk()
        root.title("F1 Fantasy Tracker 2025")
        root.geometry("1200x800")
        
        # Create main controller
        controller = MainController(root, excel_file)
        
        # Start the application
        logger.info("Starting F1 Fantasy Tracker application")
        root.mainloop()
    
    except Exception as e:
        logger.critical(f"Unhandled exception in main application: {e}", exc_info=True)
        
        # Show error dialog if GUI is available
        try:
            if 'root' in locals() and root:
                from tkinter import messagebox
                messagebox.showerror("Critical Error", 
                                    f"An unhandled error occurred: {e}\n\nSee log file for details.")
        except:
            pass
        
        # Print to console as fallback
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()