"""
controllers/main_controller.py - Main application controller
"""

import tkinter as tk
from tkinter import filedialog, ttk
import os
import logging
from datetime import datetime

from models.data_manager import F1DataManager
from views.main_view import MainView
from views.player_view import PlayerView
from views.race_view import RaceView
from views.standings_view import StandingsView
from controllers.player_controller import PlayerController
from controllers.race_controller import RaceController
from controllers.standings_controller import StandingsController
from views.visualization.season_progress import SeasonProgressVisualization
from views.visualization.points_table import PointsTableVisualization
from controllers.visualization_controller import SeasonProgressController, PointsTableController

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

class MainController:
    """
    Main application controller that coordinates between models and views.
    This controller:
    - Sets up the main view
    - Initializes all sub-controllers
    - Handles main menu commands
    - Manages application-wide operations
    """
    
    def __init__(self, root, excel_file):
        """
        Initialize the main controller.
        
        Args:
            root: The root Tk instance
            excel_file (str): Path to the Excel file
        """
        self.root = root
        self.excel_file = excel_file
        self.data_manager = F1DataManager(excel_file)
        
        # Initialize the main view
        self.view = MainView(root)
        
        self.init_views()
        self.init_controllers()

        # Connect view events to controller methods
        self.connect_view_events()
        
        # Initialize sub-controllers and their views
        self.init_player_controller()
        self.init_visualization_controllers()
        
        # Check if Excel file exists and offer to initialize if not
        self.check_excel_file()
        
        # Set status
        self.view.set_status("Ready")

    def init_controllers(self):
        """Initialize all controllers"""
        self.player_controller = PlayerController(self.player_view, self.data_manager)
        self.race_controller = RaceController(self.race_view, self.data_manager)
        self.standings_controller = StandingsController(self.standings_view, self.data_manager)
        
        # Initialize visualization controllers
        self.init_visualization_controllers()

    def init_views(self):
        """Initialize all views"""
        self.player_view = PlayerView(self.view.notebook)
        self.race_view = RaceView(self.view.notebook)
        self.standings_view = StandingsView(self.view.notebook)
        
        # Add tabs to notebook
        self.view.add_tab("Player Management", self.player_view)
        self.view.add_tab("Race Management", self.race_view)
        self.view.add_tab("Standings", self.standings_view)

    
    def connect_view_events(self):
        """Connect main view event handlers to controller methods"""
        # Connect menu handlers
        self.view.on_initialize_system = self.initialize_system
        self.view.on_backup_data = self.backup_data
        self.view.on_add_player = self.show_add_player_dialog
        self.view.on_change_driver = self.show_change_driver_dialog
        self.view.on_update_race = self.show_update_race_dialog
        self.view.on_add_substitution = self.show_add_substitution_dialog
        self.view.on_show_standings = self.show_standings
        self.view.on_show_race_breakdown = self.show_race_breakdown
        self.view.on_show_points_table = self.show_points_table
    
    def init_player_controller(self):
        """Initialize the player controller and view"""
        # Create player view
        self.player_view = PlayerView(self.view.notebook)
        
        # Create player controller
        self.player_controller = PlayerController(self.player_view, self.data_manager)
        
        # Add player tab to notebook
        self.view.add_tab("Player Management", self.player_view)
    
    def init_visualization_controllers(self):
        """Initialize visualization controllers and views"""
        # Create visualizations tab frame
        self.viz_frame = tk.Frame(self.view.notebook)
        self.view.notebook.add(self.viz_frame, text="Visualizations")
        
        # Create sub-notebook for visualizations
        self.viz_notebook = ttk.Notebook(self.viz_frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create visualization tabs
        self.season_progress_frame = tk.Frame(self.viz_notebook)
        self.points_table_frame = tk.Frame(self.viz_notebook)
        
        self.viz_notebook.add(self.season_progress_frame, text="Season Progress")
        self.viz_notebook.add(self.points_table_frame, text="Points Table")
        
        # Create visualization views
        self.season_progress_view = SeasonProgressVisualization(self.season_progress_frame, None)
        self.points_table_view = PointsTableVisualization(self.points_table_frame, None)
        
        # Create visualization controllers
        self.season_progress_controller = SeasonProgressController(self.season_progress_view, self.data_manager)
        self.points_table_controller = PointsTableController(self.points_table_view, self.data_manager)
        
        # Connect views to controllers
        self.season_progress_view.controller = self.season_progress_controller
        self.points_table_view.controller = self.points_table_controller
        
        # Initialize visualizations
        self.season_progress_controller.initialize()
        self.points_table_controller.initialize()
    
    def check_excel_file(self):
        """Check if Excel file exists and offer to initialize if not"""
        if not os.path.exists(self.excel_file):
            result = tk.messagebox.askyesno(
                "Initialize System", 
                f"The F1 Fantasy Excel file ({self.excel_file}) doesn't exist yet. Would you like to initialize the system?"
            )
            if result:
                self.initialize_system()
    
    def initialize_system(self):
        """Initialize the F1 Fantasy system"""
        result = tk.messagebox.askyesno(
            "Initialize System", 
            "This will initialize (or reset) the F1 Fantasy system with default data.\nAny existing data will be overwritten. Continue?"
        )
        if not result:
            return
        
        # Create Excel file if it doesn't exist
        if not self.data_manager.create_excel_if_not_exists():
            tk.messagebox.showerror("Error", "Failed to create Excel file")
            return
        
        # Initialize with 2025 season data
        if self.data_manager.initialize_season_data():
            tk.messagebox.showinfo("Success", "System initialized successfully")
            self.view.set_status("System initialized successfully")
            
            # Refresh player controller data
            self.player_controller.load_data()
        else:
            tk.messagebox.showerror("Error", "Failed to initialize season data")
            self.view.set_status("Failed to initialize season data")
    
    def backup_data(self):
        """Backup the Excel file"""
        # Ask for backup location
        backup_path = filedialog.asksaveasfilename(
            initialfile=f"F1_Fantasy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Backup As"
        )
        
        if not backup_path:
            return
        
        # Create backup
        result = self.data_manager.backup_excel_file(backup_path)
        if result:
            tk.messagebox.showinfo("Success", f"Backup created successfully at {backup_path}")
            self.view.set_status(f"Backup created at {backup_path}")
        else:
            tk.messagebox.showerror("Error", "Failed to create backup")
            self.view.set_status("Failed to create backup")
    
    def show_add_player_dialog(self):
        """Show dialog to add a new player"""
        # This is handled by the PlayerController
        self.view.notebook.select(self.view.notebook.index(self.player_view.frame))
    
    def show_change_driver_dialog(self):
        """Show dialog to change a driver for a player"""
        # This is handled by the PlayerController
        self.view.notebook.select(self.view.notebook.index(self.player_view.frame))
        self.player_controller.show_change_driver_dialog()
    
    def show_update_race_dialog(self):
        """Show dialog to update race results"""
        tk.messagebox.showinfo("Not Implemented", "This functionality is not yet implemented")
    
    def show_add_substitution_dialog(self):
        """Show dialog to add a driver substitution"""
        tk.messagebox.showinfo("Not Implemented", "This functionality is not yet implemented")
    
    def show_standings(self):
        """Show season standings visualization"""
        # Switch to visualizations tab and select season progress
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.season_progress_frame))
        
        # Update visualization
        self.season_progress_controller.update_visualization()
    
    def show_race_breakdown(self):
        """Show race breakdown visualization"""
        tk.messagebox.showinfo("Not Implemented", "This functionality is not yet implemented")
    
    def show_points_table(self):
        """Show points table visualization"""
        # Switch to visualizations tab and select points table
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.points_table_frame))
        
        # Update visualization
        self.points_table_controller.update_table('driver')
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
