"""
controllers/player_controller.py - Controller for player management
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlayerController:
    """
    Controller for player management.
    Handles actions related to adding players and changing driver picks.
    """
    def __init__(self, view, data_manager):
        """
        Initialize the player controller.
        
        Args:
            view: The player view
            data_manager: The data manager
        """
        self.view = view
        self.data_manager = data_manager
        
        logger.info("Initializing PlayerController")
        
        # Connect view events to controller methods
        self.connect_view_events()
        
        # Load data
        self.load_data()
        
        logger.info("PlayerController initialization completed")


    def connect_view_events(self):
        """Connect view event handlers to controller methods"""
        logger.info("Connecting player view events")
        
        # Core view event handlers
        self.view.on_add_player = self.add_player
        self.view.on_refresh_players = self.load_data
        self.view.on_change_driver = self.show_change_driver_dialog
        self.view.on_player_selected = self.player_selected
        
        # Connect driver selection events
        if hasattr(self.view, 'driver1_var') and hasattr(self.view, 'driver2_var'):
            logger.info("Connecting driver selection events")
            self.view.driver1_var.trace_add("write", self.driver1_selected)
            self.view.driver2_var.trace_add("write", self.driver2_selected)
        
        # Directly connect to button commands to ensure they work
        self.connect_buttons()
        
        logger.info("Player view events connected successfully")
    
    def connect_buttons(self):
        """Directly connect to button commands"""
        try:
            # Find the Add Player button and connect it directly
            add_button = self.find_button_by_text(self.view.frame, "Add Player")
            if add_button:
                logger.info("Found Add Player button - connecting directly")
                add_button.config(command=self.add_player)
            else:
                logger.warning("Add Player button not found in PlayerView")
                
            # Find the Refresh Players button and connect it directly
            refresh_button = self.find_button_by_text(self.view.frame, "Refresh Players")
            if refresh_button:
                logger.info("Found Refresh Players button - connecting directly")
                refresh_button.config(command=self.load_data)
            
            # Find the Change Driver button and connect it directly
            change_button = self.find_button_by_text(self.view.frame, "Change Driver")
            if change_button:
                logger.info("Found Change Driver button - connecting directly")
                change_button.config(command=self.show_change_driver_dialog)
                
        except Exception as e:
            logger.error(f"Error connecting buttons directly: {e}")
    
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
    
    def load_data(self):
        """Load data from the data manager and update the view"""
        logger.info("Loading player data")
        
        # Load data
        data = self.data_manager.load_data()
        if not data:
            logger.error("Failed to load data from data manager")
            return
        
        # Update driver dropdown options
        drivers = data['drivers']
        driver_options = [f"{row['Name']} ({row['DriverID']}) - {row['Credits']} credits" 
                         for _, row in drivers.sort_values(by='Name').iterrows()]
        logger.info(f"Setting {len(driver_options)} driver options")
        self.view.set_driver_options(driver_options)
        
        # Update player list
        self.update_player_list()
        
        logger.info("Player data loaded successfully")
    
    
    def add_player(self):
        """Add a new player"""
        logger.info("Add player method called")
        
        # Get form data
        player_id, player_name, driver1_id, driver2_id = self.view.get_form_data()
        logger.info(f"Form data: {player_id}, {player_name}, {driver1_id}, {driver2_id}")
        
        # Validate inputs
        if not player_id or not player_name:
            messagebox.showerror("Error", "Player ID and Name are required")
            return
        
        if not driver1_id or not driver2_id:
            messagebox.showerror("Error", "Two drivers must be selected")
            return
        
        # Check for duplicates
        if driver1_id == driver2_id:
            messagebox.showerror("Error", "Cannot select the same driver twice")
            return
        
        # Validate team total credits
        data = self.data_manager.load_data()
        driver1 = data['drivers'][data['drivers']['DriverID'] == driver1_id]
        driver2 = data['drivers'][data['drivers']['DriverID'] == driver2_id]
        
        if driver1.empty or driver2.empty:
            messagebox.showerror("Error", "One or more selected drivers not found")
            return
        
        total_credits = driver1['Credits'].iloc[0] + driver2['Credits'].iloc[0]
        if total_credits > 5:
            messagebox.showerror("Error", f"Team exceeds credit limit: {total_credits}/5 credits")
            return
        
        # Add player
        if self.data_manager.add_player(player_id, player_name, [driver1_id, driver2_id]):
            messagebox.showinfo("Success", f"Player {player_name} added successfully!")
            
            # Clear form
            self.view.clear_form()
            
            # Refresh player list
            self.update_player_list()
        else:
            messagebox.showerror("Error", "Failed to add player")
    
    # The rest of the PlayerController methods remain largely unchanged...
    
    def update_player_list(self):
        """Update the player list in the view"""
        logger.info("Updating player list")
        
        # Load data
        data = self.data_manager.load_data()
        if not data:
            logger.error("Failed to load data for player list update")
            return
        
        # Get player picks
        player_picks = data['player_picks']
        drivers = data['drivers']
        
        # Process player data
        players_data = []
        
        # Get active picks (ToDate is null)
        active_picks = player_picks[player_picks['ToDate'].isna()]
        
        # Get unique players
        unique_players = active_picks['PlayerID'].unique()
        logger.info(f"Found {len(unique_players)} unique players")
        
        for player_id in unique_players:
            player_data = active_picks[active_picks['PlayerID'] == player_id]
            player_name = player_data['PlayerName'].iloc[0]
            
            # Get driver names and calculate total credits
            driver_ids = player_data['DriverID'].tolist()
            driver_names = []
            total_credits = 0
            
            for driver_id in driver_ids:
                driver = drivers[drivers['DriverID'] == driver_id]
                if not driver.empty:
                    driver_names.append(f"{driver['Name'].iloc[0]} ({driver_id})")
                    total_credits += driver['Credits'].iloc[0]
            
            # Add to players data
            players_data.append((
                player_id,
                player_name,
                ', '.join(driver_names),
                total_credits
            ))
        
        # Update the view
        logger.info(f"Updating view with {len(players_data)} players")
        self.view.update_player_list(players_data)

    def driver1_selected(self, *args):
        """Handle first driver selection"""
        driver = self.view.driver1_var.get()
        if not driver:
            return
        
        # Try to extract driver ID
        try:
            driver_id = driver.split('(')[1].split(')')[0]
            self.update_driver_image(driver_id, 1)
            self.update_credit_info()
            self.update_team_preview()
        except Exception as e:
            logger.error(f"Error handling driver1 selection: {e}")
    
    def driver2_selected(self, *args):
        """Handle second driver selection"""
        driver = self.view.driver2_var.get()
        if not driver:
            return
        
        # Try to extract driver ID
        try:
            driver_id = driver.split('(')[1].split(')')[0]
            self.update_driver_image(driver_id, 2)
            self.update_credit_info()
            self.update_team_preview()
        except Exception as e:
            logger.error(f"Error handling driver2 selection: {e}")
    
    def update_driver_image(self, driver_id, position):
        """Update driver image
        
        Args:
            driver_id (str): Driver ID
            position (int): 1 for first driver, 2 for second driver
        """
        # For this simplified implementation, we'll just use placeholders
        # In a real implementation, this would load actual driver images
        
        # Placeholder implementation
        if position == 1:
            self.view.update_driver1_image(self.create_placeholder_image(f"Driver {driver_id}", (60, 60)))
        else:
            self.view.update_driver2_image(self.create_placeholder_image(f"Driver {driver_id}", (60, 60)))
    
    def update_credit_info(self):
        """Update the credit information based on selected drivers"""
        # Get selected drivers
        driver1 = self.view.driver1_var.get()
        driver2 = self.view.driver2_var.get()
        
        if not driver1 or not driver2:
            self.view.update_credit_info("Select two drivers to see credit total")
            return
        
        try:
            # Extract driver IDs from display text
            driver1_id = driver1.split('(')[1].split(')')[0]
            driver2_id = driver2.split('(')[1].split(')')[0]
            
            # Get credit values
            data = self.data_manager.load_data()
            driver1_data = data['drivers'][data['drivers']['DriverID'] == driver1_id]
            driver2_data = data['drivers'][data['drivers']['DriverID'] == driver2_id]
            
            driver1_credits = driver1_data['Credits'].iloc[0]
            driver2_credits = driver2_data['Credits'].iloc[0]
            
            total_credits = driver1_credits + driver2_credits
            
            # Update display
            if total_credits <= 5:
                self.view.update_credit_info(f"Total: {total_credits}/5 credits (Valid team)")
            else:
                self.view.update_credit_info(f"Total: {total_credits}/5 credits (Exceeds limit!)")
        except Exception as e:
            self.view.update_credit_info("Error calculating credits")
            logger.error(f"Error updating credit info: {e}")
    
    def update_team_preview(self):
        """Update the team preview"""
        # Get selected drivers
        driver1 = self.view.driver1_var.get()
        driver2 = self.view.driver2_var.get()
        
        if not driver1 or not driver2:
            return
        
        try:
            # Extract driver IDs from display text
            driver1_id = driver1.split('(')[1].split(')')[0]
            driver2_id = driver2.split('(')[1].split(')')[0]
            
            # Get driver information
            data = self.data_manager.load_data()
            driver1_data = data['drivers'][data['drivers']['DriverID'] == driver1_id]
            driver2_data = data['drivers'][data['drivers']['DriverID'] == driver2_id]
            
            # Get driver names and credits
            driver1_name = driver1_data['Name'].iloc[0]
            driver2_name = driver2_data['Name'].iloc[0]
            driver1_credits = driver1_data['Credits'].iloc[0]
            driver2_credits = driver2_data['Credits'].iloc[0]
            
            # Get team information
            driver1_team = driver1_data['DefaultTeam'].iloc[0]
            driver2_team = driver2_data['DefaultTeam'].iloc[0]
            
            # Create placeholder images
            driver1_image = self.create_placeholder_image(f"Driver {driver1_id}", (100, 100))
            driver2_image = self.create_placeholder_image(f"Driver {driver2_id}", (100, 100))
            team1_logo = self.create_placeholder_image(f"Team {driver1_team}", (60, 60))
            team2_logo = self.create_placeholder_image(f"Team {driver2_team}", (60, 60))
            
            # Update preview
            self.view.update_team_preview(
                driver1_id, driver2_id, 
                driver1_image, driver2_image, 
                driver1_name, driver2_name, 
                driver1_credits, driver2_credits,
                team1_logo, team2_logo
            )
        except Exception as e:
            logger.error(f"Error updating team preview: {e}")
    
    def player_selected(self, event):
        """Handle player selection in the treeview"""
        player_id, player_name = self.view.get_selected_player()
        if not player_id:
            return
        
        # Show selected player's team in preview
        self.show_player_team_preview(player_id)
    
    def show_player_team_preview(self, player_id):
        """Show the selected player's team in the preview
        
        Args:
            player_id (str): Player ID
        """
        try:
            # Get player's drivers
            data = self.data_manager.load_data()
            player_picks = data['player_picks']
            
            active_picks = player_picks[(player_picks['PlayerID'] == player_id) & 
                                       (player_picks['ToDate'].isna())]
            
            if active_picks.empty:
                return
            
            # Get driver IDs
            driver_ids = active_picks['DriverID'].tolist()
            
            if len(driver_ids) < 2:
                return
            
            # Update team preview using the same method
            # Get driver information
            driver1_id = driver_ids[0]
            driver2_id = driver_ids[1]
            
            driver1_data = data['drivers'][data['drivers']['DriverID'] == driver1_id]
            driver2_data = data['drivers'][data['drivers']['DriverID'] == driver2_id]
            
            # Get driver names and credits
            driver1_name = driver1_data['Name'].iloc[0]
            driver2_name = driver2_data['Name'].iloc[0]
            driver1_credits = driver1_data['Credits'].iloc[0]
            driver2_credits = driver2_data['Credits'].iloc[0]
            
            # Get team information
            driver1_team = driver1_data['DefaultTeam'].iloc[0]
            driver2_team = driver2_data['DefaultTeam'].iloc[0]
            
            # Create placeholder images
            driver1_image = self.create_placeholder_image(f"Driver {driver1_id}", (100, 100))
            driver2_image = self.create_placeholder_image(f"Driver {driver2_id}", (100, 100))
            team1_logo = self.create_placeholder_image(f"Team {driver1_team}", (60, 60))
            team2_logo = self.create_placeholder_image(f"Team {driver2_team}", (60, 60))
            
            # Update preview
            self.view.update_team_preview(
                driver1_id, driver2_id, 
                driver1_image, driver2_image, 
                driver1_name, driver2_name, 
                driver1_credits, driver2_credits,
                team1_logo, team2_logo
            )
        except Exception as e:
            logger.error(f"Error showing player team preview: {e}")
    
    def show_change_driver_dialog(self):
        """Show dialog to change a driver for a player"""
        # Get selected player
        player_id, player_name = self.view.get_selected_player()
        if not player_id:
            messagebox.showerror("Error", "Please select a player first")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.view.frame)
        dialog.title(f"Change Driver for {player_name}")
        dialog.geometry("500x350")
        dialog.transient(self.view.frame)
        dialog.grab_set()
        
        # Get current drivers
        data = self.data_manager.load_data()
        player_picks = data['player_picks']
        
        active_picks = player_picks[(player_picks['PlayerID'] == player_id) & 
                                   (player_picks['ToDate'].isna())]
        
        current_drivers = active_picks['DriverID'].tolist()
        
        # Create form elements
        ttk.Label(dialog, text=f"Current Drivers: {', '.join(current_drivers)}").pack(pady=10)
        
        # Driver selection frame
        frame = ttk.Frame(dialog)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="Select Driver to Replace:").grid(row=0, column=0, padx=5, pady=5)
        old_driver_var = tk.StringVar()
        old_driver_dropdown = ttk.Combobox(frame, textvariable=old_driver_var, state="readonly")
        old_driver_dropdown['values'] = current_drivers
        old_driver_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Old driver image placeholder
        old_driver_label = ttk.Label(frame)
        old_driver_label.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Select New Driver:").grid(row=1, column=0, padx=5, pady=5)
        new_driver_var = tk.StringVar()
        new_driver_dropdown = ttk.Combobox(frame, textvariable=new_driver_var, state="readonly")
        
        # Filter out current drivers
        drivers = data['drivers'].copy()
        drivers = drivers[~drivers['DriverID'].isin(current_drivers)]
        driver_display = [f"{row['Name']} ({row['DriverID']}) - {row['Credits']} credits" 
                         for _, row in drivers.iterrows()]
        new_driver_dropdown['values'] = driver_display
        new_driver_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # New driver image placeholder
        new_driver_label = ttk.Label(frame)
        new_driver_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Credit info
        credit_info_var = tk.StringVar()
        credit_info_var.set("Select drivers to calculate new team credit total")
        ttk.Label(dialog, textvariable=credit_info_var).pack(pady=5)
        
        # Preview canvas
        preview_canvas = tk.Canvas(dialog, bg="white", height=150)
        preview_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Update old driver image function
        def update_old_driver_image(*args):
            driver_id = old_driver_var.get()
            if not driver_id:
                return
            
            # Create placeholder image
            old_image = self.create_placeholder_image(f"Driver {driver_id}", (50, 50))
            old_driver_label.configure(image=old_image)
            dialog.old_driver_image = old_image  # Keep a reference
            
            # Update preview
            update_preview()
        
        # Update new driver image function
        def update_new_driver_image(*args):
            driver = new_driver_var.get()
            if not driver:
                return
            
            # Extract driver ID
            driver_id = driver.split('(')[1].split(')')[0]
            
            # Create placeholder image
            new_image = self.create_placeholder_image(f"Driver {driver_id}", (50, 50))
            new_driver_label.configure(image=new_image)
            dialog.new_driver_image = new_image  # Keep a reference
            
            # Update preview
            update_preview()
        
        # Update preview function
        def update_preview():
            # Clear canvas
            preview_canvas.delete("all")
            
            # Get selected old driver
            old_driver = old_driver_var.get()
            if not old_driver:
                return
            
            # Get selected new driver
            new_driver_selection = new_driver_var.get()
            if not new_driver_selection:
                return
            
            # Extract new driver ID
            new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
            
            # Get remaining driver (the one not being replaced)
            remaining_driver = [d for d in current_drivers if d != old_driver][0]
            
            # Create placeholder images
            remaining_image = self.create_placeholder_image(f"Driver {remaining_driver}", (80, 80))
            new_image = self.create_placeholder_image(f"Driver {new_driver_id}", (80, 80))
            
            # Get driver names
            remaining_name = data['drivers'][data['drivers']['DriverID'] == remaining_driver]['Name'].iloc[0]
            new_name = data['drivers'][data['drivers']['DriverID'] == new_driver_id]['Name'].iloc[0]
            
            # Display images and names
            preview_canvas.create_text(250, 10, text="New Team Preview", font=("Arial", 12, "bold"))
            
            preview_canvas.create_image(150, 40, image=remaining_image, anchor=tk.NW)
            dialog.preview_remaining_image = remaining_image  # Keep a reference
            preview_canvas.create_text(190, 130, text=f"{remaining_name} ({remaining_driver})", anchor=tk.CENTER)
            
            preview_canvas.create_image(250, 40, image=new_image, anchor=tk.NW)
            dialog.preview_new_image = new_image  # Keep a reference
            preview_canvas.create_text(290, 130, text=f"{new_name} ({new_driver_id})", anchor=tk.CENTER)
            
            # Calculate credit total
            new_driver_credits = data['drivers'][data['drivers']['DriverID'] == new_driver_id]['Credits'].iloc[0]
            remaining_driver_credits = data['drivers'][data['drivers']['DriverID'] == remaining_driver]['Credits'].iloc[0]
            
            total_credits = new_driver_credits + remaining_driver_credits
            
            # Update credit info
            if total_credits <= 5:
                credit_info_var.set(f"New team total: {total_credits}/5 credits (Valid team)")
            else:
                credit_info_var.set(f"New team total: {total_credits}/5 credits (Exceeds limit!)")
        
        # Connect update functions
        old_driver_var.trace_add("write", update_old_driver_image)
        new_driver_var.trace_add("write", update_new_driver_image)
        
        # Change driver function
        def change_driver():
            # Validate inputs
            old_driver = old_driver_var.get()
            new_driver_selection = new_driver_var.get()
            
            if not old_driver or not new_driver_selection:
                messagebox.showerror("Error", "Please select both drivers")
                return
            
            # Extract new driver ID
            new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
            
            # Get remaining driver
            remaining_driver = [d for d in current_drivers if d != old_driver][0]
            
            # Validate new team
            new_driver_credits = data['drivers'][data['drivers']['DriverID'] == new_driver_id]['Credits'].iloc[0]
            remaining_driver_credits = data['drivers'][data['drivers']['DriverID'] == remaining_driver]['Credits'].iloc[0]
            
            total_credits = new_driver_credits + remaining_driver_credits
            
            if total_credits > 5:
                messagebox.showerror("Error", f"Team exceeds credit limit: {total_credits}/5 credits")
                return
            
            # Update player pick
            if self.data_manager.update_player_pick(player_id, old_driver, new_driver_id):
                messagebox.showinfo("Success", f"Updated {player_name}'s team: {old_driver} replaced with {new_driver_id}")
                
                # Refresh player list
                self.update_player_list()
                
                # Close dialog
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update player pick")
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Change Driver", command=change_driver).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_placeholder_image(self, text, size=(60, 60)):
        """Create a placeholder image with text
        
        Args:
            text (str): Text to display
            size (tuple): Image size (width, height)
            
        Returns:
            ImageTk.PhotoImage: Placeholder image
        """
        # Create a new image with a colored background
        image = Image.new('RGB', size, color=(200, 200, 200))
        
        # This would be replaced with actual image loading in a real implementation
        
        # Convert to PhotoImage
        photo_img = ImageTk.PhotoImage(image)
        return photo_img