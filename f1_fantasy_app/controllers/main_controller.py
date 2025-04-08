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

# Visualization views
from views.visualization.season_progress import SeasonProgressVisualization
from views.visualization.points_table import PointsTableVisualization
from views.visualization.driver_performance import DriverPerformanceVisualization
from views.visualization.head_to_head import HeadToHeadVisualization
from views.visualization.team_performance import TeamPerformanceVisualization
from views.visualization.race_analysis import RaceAnalysisVisualization
from views.visualization.player_driver_points import PlayerDriverPointsVisualization
from views.visualization.credit_efficiency import CreditEfficiencyVisualization
from views.visualization.race_points_history import RacePointsHistoryVisualization
from views.visualization.points_breakdown import PointsBreakdownVisualization

# Visualization controllers
from controllers.visualization_controller import (
    SeasonProgressController, PointsTableController, DriverPerformanceController,
    HeadToHeadController, TeamPerformanceController, RaceAnalysisController,
    PlayerDriverPointsController, CreditEfficiencyController, RacePointsHistoryController,
    PointsBreakdownController
)

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
        
        # Connect visualization menu handlers
        self.view.on_show_standings = self.show_standings
        self.view.on_show_points_table = self.show_points_table
        self.view.on_show_driver_performance = self.show_driver_performance
        self.view.on_show_head_to_head = self.show_head_to_head
        self.view.on_show_team_performance = self.show_team_performance
        self.view.on_show_race_analysis = self.show_race_analysis
        self.view.on_show_player_driver_points = self.show_player_driver_points
        self.view.on_show_credit_efficiency = self.show_credit_efficiency
        self.view.on_show_race_points_history = self.show_race_points_history
        self.view.on_show_points_breakdown = self.show_points_breakdown
    
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
        
        # Create tab frames for each visualization
        self.season_progress_frame = tk.Frame(self.viz_notebook)
        self.points_table_frame = tk.Frame(self.viz_notebook)
        self.driver_performance_frame = tk.Frame(self.viz_notebook)
        self.head_to_head_frame = tk.Frame(self.viz_notebook)
        self.team_performance_frame = tk.Frame(self.viz_notebook)
        self.race_analysis_frame = tk.Frame(self.viz_notebook)
        self.player_driver_points_frame = tk.Frame(self.viz_notebook)
        self.credit_efficiency_frame = tk.Frame(self.viz_notebook)
        self.race_points_history_frame = tk.Frame(self.viz_notebook)
        self.points_breakdown_frame = tk.Frame(self.viz_notebook)
        
        # Add tabs to notebook
        self.viz_notebook.add(self.season_progress_frame, text="Season Progress")
        self.viz_notebook.add(self.points_table_frame, text="Points Table")
        self.viz_notebook.add(self.driver_performance_frame, text="Driver Performance")
        self.viz_notebook.add(self.head_to_head_frame, text="Head to Head")
        self.viz_notebook.add(self.team_performance_frame, text="Team Performance")
        self.viz_notebook.add(self.race_analysis_frame, text="Race Analysis")
        self.viz_notebook.add(self.player_driver_points_frame, text="Driver Points by Player")
        self.viz_notebook.add(self.credit_efficiency_frame, text="Credit Efficiency")
        self.viz_notebook.add(self.race_points_history_frame, text="Race Points History")
        self.viz_notebook.add(self.points_breakdown_frame, text="Points Breakdown")
        
        # Create visualization views
        self.season_progress_view = SeasonProgressVisualization(self.season_progress_frame, None)
        self.points_table_view = PointsTableVisualization(self.points_table_frame, None)
        self.driver_performance_view = DriverPerformanceVisualization(self.driver_performance_frame, None)
        self.head_to_head_view = HeadToHeadVisualization(self.head_to_head_frame, None)
        self.team_performance_view = TeamPerformanceVisualization(self.team_performance_frame, None)
        self.race_analysis_view = RaceAnalysisVisualization(self.race_analysis_frame, None)
        self.player_driver_points_view = PlayerDriverPointsVisualization(self.player_driver_points_frame, None)
        self.credit_efficiency_view = CreditEfficiencyVisualization(self.credit_efficiency_frame, None)
        self.race_points_history_view = RacePointsHistoryVisualization(self.race_points_history_frame, None)
        self.points_breakdown_view = PointsBreakdownVisualization(self.points_breakdown_frame, None)
        
        # Create visualization controllers
        self.season_progress_controller = SeasonProgressController(self.season_progress_view, self.data_manager)
        self.points_table_controller = PointsTableController(self.points_table_view, self.data_manager)
        self.driver_performance_controller = DriverPerformanceController(self.driver_performance_view, self.data_manager)
        self.head_to_head_controller = HeadToHeadController(self.head_to_head_view, self.data_manager)
        self.team_performance_controller = TeamPerformanceController(self.team_performance_view, self.data_manager)
        self.race_analysis_controller = RaceAnalysisController(self.race_analysis_view, self.data_manager)
        self.player_driver_points_controller = PlayerDriverPointsController(self.player_driver_points_view, self.data_manager)
        self.credit_efficiency_controller = CreditEfficiencyController(self.credit_efficiency_view, self.data_manager)
        self.race_points_history_controller = RacePointsHistoryController(self.race_points_history_view, self.data_manager)
        self.points_breakdown_controller = PointsBreakdownController(self.points_breakdown_view, self.data_manager)
        
        # Connect views to controllers
        self.season_progress_view.controller = self.season_progress_controller
        self.points_table_view.controller = self.points_table_controller
        self.driver_performance_view.controller = self.driver_performance_controller
        self.head_to_head_view.controller = self.head_to_head_controller
        self.team_performance_view.controller = self.team_performance_controller
        self.race_analysis_view.controller = self.race_analysis_controller
        self.player_driver_points_view.controller = self.player_driver_points_controller
        self.credit_efficiency_view.controller = self.credit_efficiency_controller
        self.race_points_history_view.controller = self.race_points_history_controller
        self.points_breakdown_view.controller = self.points_breakdown_controller
        
        # Initialize visualizations
        self.season_progress_controller.initialize()
        self.points_table_controller.initialize()
        self.driver_performance_controller.initialize()
        self.head_to_head_controller.initialize()
        self.team_performance_controller.initialize()
        self.race_analysis_controller.initialize()
        self.player_driver_points_controller.initialize()
        self.credit_efficiency_controller.initialize()
        self.race_points_history_controller.initialize()
        self.points_breakdown_controller.initialize()
    
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
    
    def show_driver_performance(self):
        """Show driver performance visualization"""
        # Switch to visualizations tab and select driver performance
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.driver_performance_frame))
        
        # Initialize visualization if needed
        self.driver_performance_controller.initialize()

    def show_head_to_head(self):
        """Show head-to-head comparison visualization"""
        # Switch to visualizations tab and select head to head
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.head_to_head_frame))
        
        # Initialize visualization if needed
        self.head_to_head_controller.initialize()

    def show_team_performance(self):
        """Show team performance visualization"""
        # Switch to visualizations tab and select team performance
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.team_performance_frame))
        
        # Initialize visualization if needed
        self.team_performance_controller.initialize()

    def show_race_analysis(self):
        """Show race analysis dashboard"""
        # Switch to visualizations tab and select race analysis
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.race_analysis_frame))
        
        # Initialize visualization if needed
        self.race_analysis_controller.initialize()

    def show_player_driver_points(self):
        """Show player driver points visualization"""
        # Switch to visualizations tab and select player driver points
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.player_driver_points_frame))
        
        # Initialize visualization if needed
        self.player_driver_points_controller.initialize()

    def show_credit_efficiency(self):
        """Show credit efficiency visualization"""
        # Switch to visualizations tab and select credit efficiency
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.credit_efficiency_frame))
        
        # Initialize visualization if needed
        self.credit_efficiency_controller.initialize()

    def show_race_points_history(self):
        """Show race points history visualization"""
        # Switch to visualizations tab and select race points history
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.race_points_history_frame))
        
        # Initialize visualization if needed
        self.race_points_history_controller.initialize()

    def show_points_breakdown(self):
        """Show points breakdown visualization"""
        # Switch to visualizations tab and select points breakdown
        self.view.notebook.select(self.view.notebook.index(self.viz_frame))
        self.viz_notebook.select(self.viz_notebook.index(self.points_breakdown_frame))
        
        # Initialize visualization if needed
        self.points_breakdown_controller.initialize()

    def run(self):
        """Run the application"""
        self.root.mainloop()

