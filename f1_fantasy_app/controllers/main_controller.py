"""
controllers/main_controller.py - Main application controller with debugging
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
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

# Import debug utilities
from utils.debug_utils import debug_trace, debug_print_structure, debug_popup, inspect_tkinter_widget

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
    format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s',
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

    @debug_trace
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
        
        logger.info("Initializing MainController")
        
        # Initialize the main view first
        self.view = MainView(root)
        
        # Initialize views second
        self.init_views()
        
        # Initialize controllers third and connect their view events
        self.init_controllers()
        
        # Connect main view events fourth (AFTER controllers are set up)
        self.connect_view_events()
        
        # Initialize visualization controllers
        self.init_visualization_controllers()
        
        # Make sure all controllers connect their view events
        self.ensure_all_view_connections()

        # Check if Excel file exists and offer to initialize if not
        self.check_excel_file()
        
        # Rebuild menu to ensure all connections work
        self.rebuild_main_menu()

        # Set status
        self.view.set_status("Ready")
        logger.info("MainController initialization completed")

    def _debug_menu_structure(self):
        """Debug the menu structure"""
        logger.debug("Menu structure:")
        try:
            menu = self.view.root.nametowidget('.menubar')
            logger.debug(f"Main menu bar: {menu}")
            for i in range(menu.index('end') + 1):
                logger.debug(f"Menu {i}: {menu.entrycget(i, 'label')}")
                
                # Try to get submenu
                try:
                    submenu = menu.nametowidget(menu.entrycget(i, "menu"))
                    logger.debug(f"  Submenu: {submenu}")
                    for j in range(submenu.index('end') + 1):
                        try:
                            logger.debug(f"    Item {j}: {submenu.entrycget(j, 'label')}")
                        except:
                            logger.debug(f"    Item {j}: {submenu.type(j)}")
                except Exception as e:
                    logger.debug(f"  Error accessing submenu: {e}")
        except Exception as e:
            logger.debug(f"Error debugging menu: {e}")

    def init_views(self):
        """Initialize all views"""
        logger.info("Initializing views")
        self.player_view = PlayerView(self.view.notebook)
        self.race_view = RaceView(self.view.notebook)
        self.standings_view = StandingsView(self.view.notebook)
        
        # Add tabs to notebook
        self.view.add_tab("Player Management", self.player_view)
        self.view.add_tab("Race Management", self.race_view)
        self.view.add_tab("Standings", self.standings_view)
        
        logger.info("Views initialized successfully")
        
    def init_controllers(self):
        """Initialize all controllers"""
        logger.info("Initializing controllers")

        # Create controllers for all views
        self.player_controller = PlayerController(self.player_view, self.data_manager)
        self.race_controller = RaceController(self.race_view, self.data_manager)
        self.standings_controller = StandingsController(self.standings_view, self.data_manager)
        
        logger.info("Controllers initialized successfully")
    

    def connect_view_events(self):
        """Connect main view event handlers to controller methods"""
        logger.info("Connecting main view events to controller")
        
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
        
        logger.info("Main view events connected successfully")

    def ensure_all_view_connections(self):
        """Make sure all controllers have connected their view events"""
        logger.info("Ensuring all view connections")
        
        # Make sure controllers connect their view events
        if hasattr(self.player_controller, 'connect_view_events'):
            self.player_controller.connect_view_events()
            
        if hasattr(self.race_controller, 'connect_view_events'):
            self.race_controller.connect_view_events()
            
        if hasattr(self.standings_controller, 'connect_view_events'):
            self.standings_controller.connect_view_events()
            
        # Ensure button commands are directly connected
        self.ensure_button_connections()
        
        logger.info("All view connections ensured")
    
    def ensure_button_connections(self):
        """Ensure critical buttons are connected properly"""
        logger.info("Ensuring button connections")
        
        # Fix player view's "Add Player" button
        if hasattr(self.player_view, 'on_add_player'):
            add_button = self.find_button_by_text(self.player_view.frame, "Add Player")
            if add_button:
                logger.info("Found Add Player button in PlayerView")
                add_button.config(command=self.player_controller.add_player)
        
        # Fix change driver button
        change_button = self.find_button_by_text(self.player_view.frame, "Change Driver")
        if change_button:
            logger.info("Found Change Driver button in PlayerView")
            change_button.config(command=self.player_controller.show_change_driver_dialog)
            
        # Fix race view buttons
        update_race_button = self.find_button_by_text(self.race_view.frame, "Scrape & Update Results")
        if update_race_button:
            logger.info("Found Update Race button in RaceView")
            update_race_button.config(command=self.race_controller.update_race_results)
            
        add_sub_button = self.find_button_by_text(self.race_view.frame, "Add Substitution")
        if add_sub_button:
            logger.info("Found Add Substitution button in RaceView")
            add_sub_button.config(command=self.race_controller.add_substitution)
            
        # Fix standings view buttons
        show_standings_button = self.find_button_by_text(self.standings_view.frame, "Show Season Standings")
        if show_standings_button:
            logger.info("Found Show Standings button in StandingsView")
            show_standings_button.config(command=self.standings_controller.show_standings)
            
        show_breakdown_button = self.find_button_by_text(self.standings_view.frame, "Show Race Breakdown")
        if show_breakdown_button:
            logger.info("Found Show Race Breakdown button in StandingsView")
            show_breakdown_button.config(command=self.standings_controller.show_race_breakdown)
            
        logger.info("Button connections ensured")
    
    def find_button_by_text(self, parent, text):
        """
        Recursively search for a button with specific text
        
        Args:
            parent: Parent widget to search in
            text: Button text to search for
            
        Returns:
            Button widget or None if not found
        """
        # Check if this widget has the target text
        if hasattr(parent, 'cget') and hasattr(parent, 'winfo_class'):
            try:
                if parent.winfo_class() in ('TButton', 'Button') and parent.cget('text') == text:
                    return parent
            except:
                pass  # Not all widgets have text or winfo_class
        
        # Check all children
        for child in parent.winfo_children():
            result = self.find_button_by_text(child, text)
            if result:
                return result
        
        return None
    
    def rebuild_main_menu(self):
        """Rebuild the main menu to ensure all connections work"""
        logger.info("Rebuilding main menu")
        
        # Create fresh menu
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Initialize System", command=self.initialize_system)
        file_menu.add_command(label="Backup Data", command=self.backup_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Players menu
        player_menu = tk.Menu(menubar, tearoff=0)
        player_menu.add_command(label="Add New Player", command=self.show_add_player_dialog)
        player_menu.add_command(label="Change Driver Pick", command=self.show_change_driver_dialog)
        menubar.add_cascade(label="Players", menu=player_menu)
        
        # Races menu
        race_menu = tk.Menu(menubar, tearoff=0)
        race_menu.add_command(label="Update Race Results", command=self.show_update_race_dialog)
        race_menu.add_command(label="Add Driver Substitution", command=self.show_add_substitution_dialog)
        menubar.add_cascade(label="Races", menu=race_menu)
        
        # Visualizations menu
        viz_menu = tk.Menu(menubar, tearoff=0)
        viz_menu.add_command(label="Season Standings", command=self.show_standings)
        viz_menu.add_command(label="Points Table", command=self.show_points_table)
        viz_menu.add_command(label="Driver Performance", command=self.show_driver_performance)
        viz_menu.add_command(label="Head to Head Comparison", command=self.show_head_to_head)
        viz_menu.add_command(label="Team Performance", command=self.show_team_performance)
        viz_menu.add_command(label="Race Analysis", command=self.show_race_analysis)
        viz_menu.add_command(label="Driver Points by Player", command=self.show_player_driver_points)
        viz_menu.add_command(label="Credit Efficiency", command=self.show_credit_efficiency)
        viz_menu.add_command(label="Race Points History", command=self.show_race_points_history)
        viz_menu.add_command(label="Points Breakdown", command=self.show_points_breakdown)
        menubar.add_cascade(label="Visualizations", menu=viz_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Update root's menu
        self.root.config(menu=menubar)
        
        logger.info("Main menu rebuilt successfully")
    
    def show_add_player_dialog(self):
        """Show dialog to add a new player"""
        logger.info("Show add player dialog called")
        
        # Switch to the Player Management tab
        self.view.notebook.select(self.view.notebook.index(self.player_view.frame))
        
        # Clear any existing form data for a fresh start
        self.player_view.clear_form()
        
        # Provide a visual cue to the user
        self.view.set_status("Ready to add a new player - fill in the details and click 'Add Player'")
        
        # Make sure Add Player button has the correct command
        add_button = self.find_button_by_text(self.player_view.frame, "Add Player")
        if add_button:
            add_button.config(command=self.player_controller.add_player)
            
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
    
    def show_change_driver_dialog(self):
        """Show dialog to change a driver for a player"""
        # This is handled by the PlayerController
        self.view.notebook.select(self.view.notebook.index(self.player_view.frame))
        self.player_controller.show_change_driver_dialog()
    
    def show_update_race_dialog(self):
        """Show dialog to update race results"""
        # Switch to Race Management tab
        self.view.notebook.select(self.view.notebook.index(self.race_view.frame))
        
        # Get next race to update
        data = self.data_manager.load_data()
        if not data:
            tk.messagebox.showerror("Error", "Failed to load data")
            return
            
        # Find next race that needs results
        races = data['races']
        upcoming_races = races[races['Status'] == 'Upcoming'].sort_values(by='Date')
        
        if not upcoming_races.empty:
            next_race = upcoming_races.iloc[0]
            # Pre-select the race in the dropdown
            race_id = next_race['RaceID']
            race_name = next_race['Name']
            race_selection = f"{race_id} - {race_name}"
            
            if race_selection in self.race_view.race_selector['values']:
                self.race_view.update_race_var.set(race_selection)
                
            # Focus on the manual entry button since that's most likely what's needed
            self.race_controller.show_manual_point_entry()
        else:
            tk.messagebox.showinfo("Information", "All races have been updated")
    
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
        # Switch to Standings tab
        self.view.notebook.select(self.view.notebook.index(self.standings_view.frame))
        
        # Get most recent race
        data = self.data_manager.load_data()
        if not data:
            tk.messagebox.showerror("Error", "Failed to load data")
            return
        
        races = data['races']
        completed_races = races[races['Status'] == 'Completed'].sort_values(by='Date', ascending=False)
        
        if not completed_races.empty:
            last_race = completed_races.iloc[0]
            race_id = last_race['RaceID']
            race_name = last_race['Name']
            race_selection = f"{race_id} - {race_name}"
            
            # Pre-select race in dropdown
            if race_selection in self.standings_view.race_dropdown['values']:
                self.standings_view.race_var.set(race_selection)
                
            # Trigger the breakdown visualization
            self.standings_controller.show_race_breakdown()
        else:
            tk.messagebox.showinfo("Information", "No completed races found")
    
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

    # For testing, add a simple method that can be called directly
    def test_add_player(self):
        """Test method to directly add a player for debugging"""
        logger.debug("Test add player method called")
        debug_popup("Test Add Player called")
        
        # Direct the controller to add a test player
        test_player_id = "TEST1"
        test_player_name = "Test Player"
        test_driver_ids = ["VER", "HAM"]  # Example driver IDs
        
        # Call the data manager directly
        result = self.data_manager.add_player(test_player_id, test_player_name, test_driver_ids)
        
        if result:
            messagebox.showinfo("Success", f"Test player {test_player_name} added successfully!")
            # Refresh player list
            self.player_controller.update_player_list()
        else:
            messagebox.showerror("Error", "Failed to add test player")