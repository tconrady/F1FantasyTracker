"""
views/dialogs/change_driver_dialog.py - Dialog for changing a player's driver
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class ChangeDriverDialog:
    """Dialog for changing a player's driver pick"""
    
    def __init__(self, parent, player_id, player_name, current_drivers, 
                 available_drivers, driver_images=None, callback=None):
        """
        Initialize the change driver dialog.
        
        Args:
            parent: Parent window
            player_id (str): Player's ID
            player_name (str): Player's name
            current_drivers (list): List of current driver IDs
            available_drivers (list): List of available driver options
            driver_images (dict, optional): Dictionary with driver images
            callback (function, optional): Function to call on successful change
        """
        self.parent = parent
        self.player_id = player_id
        self.player_name = player_name
        self.current_drivers = current_drivers
        self.available_drivers = available_drivers
        self.driver_images = driver_images or {}
        self.callback = callback
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Change Driver for {player_name}")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.connect_events()
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Current drivers label
        ttk.Label(self.dialog, text=f"Current Drivers: {', '.join(self.current_drivers)}").pack(pady=10)
        
        # Create form elements
        frame = ttk.Frame(self.dialog)
        frame.pack(pady=10)
        
        ttk.Label(frame, text="Select Driver to Replace:").grid(row=0, column=0, padx=5, pady=5)
        self.old_driver_var = tk.StringVar()
        self.old_driver_dropdown = ttk.Combobox(frame, textvariable=self.old_driver_var, state="readonly")
        self.old_driver_dropdown['values'] = self.current_drivers
        self.old_driver_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        # Old driver image placeholder
        self.old_driver_label = ttk.Label(frame)
        self.old_driver_label.grid(row=0, column=2, padx=5, pady=5)
        
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
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Change Driver", command=self.change_driver).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def connect_events(self):
        """Connect event handlers"""
        self.old_driver_var.trace_add("write", self.update_old_driver_image)
        self.new_driver_var.trace_add("write", self.update_new_driver_image)
        self.old_driver_var.trace_add("write", self.update_dialog_credit_info)
        self.new_driver_var.trace_add("write", self.update_dialog_credit_info)
    
    def update_old_driver_image(self, *args):
        """Update the old driver image"""
        driver_id = self.old_driver_var.get()
        if not driver_id:
            return
        
        if driver_id in self.driver_images:
            self.old_driver_label.configure(image=self.driver_images[driver_id])
        else:
            self.old_driver_label.configure(image='')
        
        self.update_preview()
    
    def update_new_driver_image(self, *args):
        """Update the new driver image"""
        new_driver = self.new_driver_var.get()
        if not new_driver:
            return
        
        # Extract driver ID
        driver_id = new_driver.split('(')[1].split(')')[0]
        
        if driver_id in self.driver_images:
            self.new_driver_label.configure(image=self.driver_images[driver_id])
        else:
            self.new_driver_label.configure(image='')
        
        self.update_preview()
    
    def update_preview(self):
        """Update the team preview"""
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Get selected old and new drivers
        old_driver = self.old_driver_var.get()
        new_driver_selection = self.new_driver_var.get()
        
        if not old_driver or not new_driver_selection:
            return
        
        # Extract new driver ID
        new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
        
        # Get remaining driver (the one not being replaced)
        remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
        
        # Display preview
        self.preview_canvas.create_text(250, 10, text="New Team Preview", font=("Arial", 12, "bold"))
        
        # Add remaining driver and new driver images/info
        # This is simplified - in a real implementation you would use actual driver images
        
        # Update credit info based on driver data
        self.update_dialog_credit_info()
    
    def update_dialog_credit_info(self, *args):
        """Update credit info in the dialog"""
        # Get selected old driver
        old_driver = self.old_driver_var.get()
        new_driver = self.new_driver_var.get()
        
        if not old_driver or not new_driver:
            self.credit_info_var.set("Select drivers to calculate new team credit total")
            return
        
        # Extract new driver ID and get its credits
        new_driver_id = new_driver.split('(')[1].split(')')[0]
        new_driver_credits = float(new_driver.split('- ')[1].split(' credits')[0])
        
        # Get remaining driver (the one not being replaced)
        remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
        
        # Calculate new credit total
        # In a real implementation you would get these from data, this is simplified
        remaining_driver_credits = 2.0  # Placeholder
        
        total_credits = new_driver_credits + remaining_driver_credits
        
        # Update display
        if total_credits <= 5:
            self.credit_info_var.set(f"New team total: {total_credits}/5 credits (Valid team)")
        else:
            self.credit_info_var.set(f"New team total: {total_credits}/5 credits (Exceeds limit!)")
    
    def change_driver(self):
        """Process the driver change"""
        # Validate inputs
        old_driver = self.old_driver_var.get()
        new_driver_selection = self.new_driver_var.get()
        
        if not old_driver or not new_driver_selection:
            messagebox.showerror("Error", "Please select both drivers")
            return
        
        # Extract new driver ID
        new_driver_id = new_driver_selection.split('(')[1].split(')')[0]
        
        # Get remaining driver
        remaining_driver = [d for d in self.current_drivers if d != old_driver][0]
        
        # Validate new team
        # In a real implementation, you would check credit total here
        
        # Execute callback if provided
        if self.callback:
            result = self.callback(old_driver, new_driver_id)
            if result:
                self.dialog.destroy()
        else:
            self.dialog.destroy()