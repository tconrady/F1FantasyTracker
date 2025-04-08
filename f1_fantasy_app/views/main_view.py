"""
views/main_view.py - Main application view that contains all other views
"""

import tkinter as tk
from tkinter import ttk, Menu, messagebox

class MainView:
    """Main application view class"""
    
    def __init__(self, root):
        """
        Initialize the main view.
        
        Args:
            root: The root Tk instance
        """
        self.root = root
        self.root.title("F1 Fantasy Tracker 2025")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Create a status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create main menu
        self.create_menu()
        
    def create_menu(self):
        """Create the main menu bar"""
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Initialize System", command=self.on_initialize_system)
        file_menu.add_command(label="Backup Data", command=self.on_backup_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Players menu
        player_menu = Menu(menubar, tearoff=0)
        player_menu.add_command(label="Add New Player", command=self.on_add_player)
        player_menu.add_command(label="Change Driver Pick", command=self.on_change_driver)
        menubar.add_cascade(label="Players", menu=player_menu)
        
        # Races menu
        race_menu = Menu(menubar, tearoff=0)
        race_menu.add_command(label="Update Race Results", command=self.on_update_race)
        race_menu.add_command(label="Add Driver Substitution", command=self.on_add_substitution)
        menubar.add_cascade(label="Races", menu=race_menu)
        
        # Visualizations menu
        viz_menu = Menu(menubar, tearoff=0)
        viz_menu.add_command(label="Season Standings", command=self.on_show_standings)
        viz_menu.add_command(label="Points Table", command=self.on_show_points_table)
        viz_menu.add_command(label="Driver Performance", command=self.on_show_driver_performance)
        viz_menu.add_command(label="Head to Head Comparison", command=self.on_show_head_to_head)
        viz_menu.add_command(label="Team Performance", command=self.on_show_team_performance)
        viz_menu.add_command(label="Race Analysis", command=self.on_show_race_analysis)
        viz_menu.add_command(label="Driver Points by Player", command=self.on_show_player_driver_points)
        viz_menu.add_command(label="Credit Efficiency", command=self.on_show_credit_efficiency)
        viz_menu.add_command(label="Race Points History", command=self.on_show_race_points_history)
        viz_menu.add_command(label="Points Breakdown", command=self.on_show_points_breakdown)
        menubar.add_cascade(label="Visualizations", menu=viz_menu)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.on_show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def add_tab(self, title, view):
        """Add a new tab with a view
        
        Args:
            title (str): Tab title
            view: View instance to add
        """
        self.notebook.add(view.frame, text=title)
        
    def set_status(self, message):
        """Set the status bar message
        
        Args:
            message (str): Status message
        """
        self.status_var.set(message)
        
    # Menu command handlers - these will be linked to controllers
    def on_initialize_system(self):
        """Initialize system command handler"""
        messagebox.showinfo("Initialize System", "This will be implemented by the controller")
        
    def on_backup_data(self):
        """Backup data command handler"""
        messagebox.showinfo("Backup Data", "This will be implemented by the controller")
        
    def on_add_player(self):
        """Add player command handler"""
        messagebox.showinfo("Add Player", "This will be implemented by the controller")
        
    def on_change_driver(self):
        """Change driver command handler"""
        messagebox.showinfo("Change Driver", "This will be implemented by the controller")
        
    def on_update_race(self):
        """Update race command handler"""
        messagebox.showinfo("Update Race", "This will be implemented by the controller")
        
    def on_add_substitution(self):
        """Add substitution command handler"""
        messagebox.showinfo("Add Substitution", "This will be implemented by the controller")
        
    def on_show_standings(self):
        """Show standings command handler"""
        messagebox.showinfo("Show Standings", "This will be implemented by the controller")
        
    def on_show_race_breakdown(self):
        """Show race breakdown command handler"""
        messagebox.showinfo("Show Race Breakdown", "This will be implemented by the controller")
        
    def on_show_points_table(self):
        """Show points table command handler"""
        messagebox.showinfo("Show Points Table", "This will be implemented by the controller")
        
    def on_show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About F1 Fantasy Tracker", 
                           "F1 Fantasy Tracker 2025\n\n"
                           "A tool to track your F1 Fantasy League performance.")
        
    def on_show_driver_performance(self):
        """Show driver performance visualization handler"""
        messagebox.showinfo("Show Driver Performance", "This will be implemented by the controller")

    def on_show_head_to_head(self):
        """Show head-to-head comparison visualization handler"""
        messagebox.showinfo("Show Head to Head", "This will be implemented by the controller")

    def on_show_team_performance(self):
        """Show team performance visualization handler"""
        messagebox.showinfo("Show Team Performance", "This will be implemented by the controller")

    def on_show_race_analysis(self):
        """Show race analysis visualization handler"""
        messagebox.showinfo("Show Race Analysis", "This will be implemented by the controller")

    def on_show_player_driver_points(self):
        """Show player driver points visualization handler"""
        messagebox.showinfo("Show Driver Points by Player", "This will be implemented by the controller")

    def on_show_credit_efficiency(self):
        """Show credit efficiency visualization handler"""
        messagebox.showinfo("Show Credit Efficiency", "This will be implemented by the controller")

    def on_show_race_points_history(self):
        """Show race points history visualization handler"""
        messagebox.showinfo("Show Race Points History", "This will be implemented by the controller")

    def on_show_points_breakdown(self):
        """Show points breakdown visualization handler"""
        messagebox.showinfo("Show Points Breakdown", "This will be implemented by the controller")