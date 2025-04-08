"""
views/dialogs/change_driver_dialog.py - Dialog for changing a player's driver
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ChangeDriverDialog:
    """Dialog for changing a player's driver pick"""
    
    def __init__(self, parent, player_id, player_name, current_drivers, 
                 available_drivers, driver_data, image_loader, on_confirm=None):
        """
        Initialize the change driver dialog.
        
        Args:
            parent: The parent widget
            player_id (str): Player ID
            player_name (str): Player name
            current_drivers (list): List of current driver IDs
            available_drivers (list): List of available driver options in display format
            driver_data (dict): Dictionary containing driver data for lookups
            image_loader: The image loader instance for driver images
            on_confirm (callable, optional): Function to call when change is confirmed
        """
        self.parent = parent
        self.player_id = player_id
        self.player_name = player_name
        self.current_drivers = current_drivers
        self.available_drivers = available_drivers
        self.driver_data = driver_data
        self.image_loader = image_loader
        self.on_confirm = on_confirm
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Change Driver for {player_name}")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create dialog elements
        self._create_widgets()
        
        # Store references to images to prevent garbage collection
        self.images = {}
    
    def _create_widgets(self):
        """Create all dialog widgets"""
        # Title label
        ttk.Label(self.dialog, text=f"Current Drivers: {', '.join(self.current_drivers)}").pack(pady=10)
        
        # Driver selection frame
        frame = ttk.Frame(self.dialog)
        frame.pack(pady=10)
        
        # Old driver selection
        ttk.Label(frame, text="Select Driver to Replace:").grid(row=0, column=0, padx=5, pady=5)
        self.old_driver_var = tk.StringVar()
        self.old_driver_dropdown = ttk.Combobox(frame, textvariable=self.old_driver_var, state="readonly")
        self.old_driver_dropdown['values'] = self.current_drivers
        self.old_driver_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Old driver image placeholder
        self.old_driver_label = ttk.Label(frame)
        self.old_driver_label.grid(row=0, column=2, padx=5, pady=5)
        
        # New driver selection
        ttk.Label(frame, text="Select New Driver:").grid(row=1, column=0, padx=5, pady=5)
        self.new_driver_var = tk.StringVar()
        self.new_driver_dropdown = ttk.Combobox(frame, textvariable=self.new_driver_var, state="readonly")
        self.new_driver_dropdown['values'] = self.available_drivers
        self.new_driver_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        # New driver image placeholder
        self.new_driver_label = ttk.Label(frame)
        self.new_driver_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Credit info
        self.credit_info_var = tk.StringVar()
        self.credit_info_var.set("Select drivers to calculate new team credit total")
        ttk.Label(self.dialog, textvariable=self.credit_info_var).pack(pady=5)
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(self.dialog, bg="white", height=150)
        self.preview_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Change Driver", command=self._on_change).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Connect update functions
        self.old_driver_var.trace_add("write", self._update_old_driver_image)
        self.new_driver_var.trace_add("write", self._update_new_driver_image)
        self.old_driver_var.trace_add("write", self._update_credit_info)
        self.new_driver_var.trace_add("write", self._update_credit_info)
    
    def _update_old_driver_image(self, *args):
        """Update the old driver image when selection changes"""
        driver_id = self.old_driver_var.get()
        if not driver_id:
            return
        
        # Get driver image
        driver_image = self.image_loader.get_driver_image(driver_id, size=(50, 50))
        
        if driver_image:
            self.old_driver_label.configure(image=driver_image)
            self.images["old_driver"] = driver_image  # Keep reference
        else:
            placeholder = self.image_loader.create_placeholder_image(f"Driver {driver_id}", size=(50, 50))
            self.old_driver_label.configure(image=placeholder)
            self.images["old_driver"] = placeholder  # Keep reference
        
        # Update preview
        self._update_preview()
    
    def _update_new_driver_image(self, *args):
        """Update the new driver image when selection changes"""
        driver_selection = self.new_driver_var.get()
        if not driver_selection:
            return
        
        # Extract driver ID
        driver_id = driver_selection.split('(')[1].split(')')[0]
        
        # Get driver image
        driver_image = self.image_loader.get_driver_image(driver_id, size=(50, 50))
        
        if driver_image:
            self.new_driver_label.configure(image=driver_image)
            self.images["new_driver"] = driver_image  # Keep reference
        else:
            placeholder = self.image_loader.create_placeholder_image(f"Driver {driver_id}", size=(50, 50))
            self.new_driver_label.configure(image=placeholder)
            self.images["new_driver"] = placeholder  # Keep reference
        
        # Update preview
        self._update_preview()
    
    def _update_credit_info(self, *args):
        """Update credit info when selections change"""
        old_driver = self.old_driver_var.get()
        new_driver_selection = self.new_driver_var.get()
        
        if not old_driver or not new_driver_selection:
            self.credit_info_var.set("Select drivers to calculate new team credit total")
            return
        
        try:
            # Extract new driver ID
            new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
            
            # Get remaining driver (the one not being replaced)
            remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
            
            # Calculate new credit total
            new_driver_credits = self._get_driver_credits(new_driver_id)
            remaining_driver_credits = self._get_driver_credits(remaining_driver)
            
            total_credits = new_driver_credits + remaining_driver_credits
            
            # Update display
            if total_credits <= 5:
                self.credit_info_var.set(f"New team total: {total_credits}/5 credits (Valid team)")
            else:
                self.credit_info_var.set(f"New team total: {total_credits}/5 credits (Exceeds limit!)")
        except Exception as e:
            self.credit_info_var.set("Error calculating credits")
            print(f"Error updating credit info: {e}")
    
    def _update_preview(self):
        """Update the team preview canvas"""
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Get selected old driver
        old_driver = self.old_driver_var.get()
        if not old_driver:
            return
        
        # Get selected new driver
        new_driver_selection = self.new_driver_var.get()
        if not new_driver_selection:
            return
        
        # Extract new driver ID
        new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
        
        # Get remaining driver (the one not being replaced)
        remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
        
        # Get driver images
        remaining_image = self.image_loader.get_driver_image(remaining_driver, (80, 80))
        new_image = self.image_loader.get_driver_image(new_driver_id, (80, 80))
        
        if not remaining_image:
            remaining_image = self.image_loader.create_placeholder_image(f"Driver {remaining_driver}", (80, 80))
        if not new_image:
            new_image = self.image_loader.create_placeholder_image(f"Driver {new_driver_id}", (80, 80))
        
        # Store references to prevent garbage collection
        self.images["remaining_image"] = remaining_image
        self.images["new_image"] = new_image
        
        # Get driver names
        remaining_name = self._get_driver_name(remaining_driver)
        new_name = self._get_driver_name(new_driver_id)
        
        # Display images and names
        self.preview_canvas.create_text(250, 10, text="New Team Preview", font=("Arial", 12, "bold"))
        
        self.preview_canvas.create_image(150, 40, image=remaining_image, anchor=tk.NW)
        self.preview_canvas.create_text(190, 130, text=f"{remaining_name} ({remaining_driver})", anchor=tk.CENTER)
        
        self.preview_canvas.create_image(250, 40, image=new_image, anchor=tk.NW)
        self.preview_canvas.create_text(290, 130, text=f"{new_name} ({new_driver_id})", anchor=tk.CENTER)
    
    def _get_driver_credits(self, driver_id):
        """Get driver credits from driver data"""
        for _, driver in self.driver_data.iterrows():
            if driver['DriverID'] == driver_id:
                return driver['Credits']
        return 0
    
    def _get_driver_name(self, driver_id):
        """Get driver name from driver data"""
        for _, driver in self.driver_data.iterrows():
            if driver['DriverID'] == driver_id:
                return driver['Name']
        return driver_id
    
    def _on_change(self):
        """Handle change driver button click"""
        old_driver = self.old_driver_var.get()
        new_driver_selection = self.new_driver_var.get()
        
        if not old_driver or not new_driver_selection:
            from tkinter import messagebox
            messagebox.showerror("Error", "Please select both drivers")
            return
        
        # Extract new driver ID
        new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
        
        # Get remaining driver
        remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
        
        # Validate new team credits
        new_driver_credits = self._get_driver_credits(new_driver_id)
        remaining_driver_credits = self._get_driver_credits(remaining_driver)
        
        total_credits = new_driver_credits + remaining_driver_credits
        
        if total_credits > 5:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Team exceeds credit limit: {total_credits}/5 credits")
            return
        
        # Call confirm function if provided
        if self.on_confirm:
            self.on_confirm(self.player_id, old_driver, new_driver_id)
        
        # Close dialog
        self.dialog.destroy()