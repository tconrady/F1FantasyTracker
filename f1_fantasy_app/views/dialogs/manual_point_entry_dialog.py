"""
views/dialogs/manual_point_entry_dialog.py - Dialog for manually entering race points
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ManualPointEntryDialog:
    """Dialog for manual entry of driver points for a race"""
    
    def __init__(self, parent, race_id, drivers_data, callback=None):
        """
        Initialize the manual point entry dialog.
        
        Args:
            parent: Parent window
            race_id (str): Race ID
            drivers_data (list): List of driver data dictionaries
            callback (function, optional): Function to call with results
        """
        self.parent = parent
        self.race_id = race_id
        self.drivers_data = drivers_data
        self.callback = callback
        self.point_vars = {}  # Will store StringVars for point inputs
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Manual Point Entry for {race_id}")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        ttk.Label(self.dialog, text=f"Enter fantasy points for each driver for {self.race_id}").pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create entry fields for each driver
        ttk.Label(scrollable_frame, text="Driver").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Points").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="").grid(row=0, column=2, padx=5, pady=5)  # For images
        
        for i, driver in enumerate(self.drivers_data, 1):
            driver_id = driver['DriverID']
            driver_name = driver['Name']
            
            # Driver image (placeholder in this implementation)
            if 'image' in driver:
                image_label = ttk.Label(scrollable_frame, image=driver['image'])
                image_label.grid(row=i, column=2, padx=5, pady=2)
                # Store reference to prevent garbage collection
                setattr(self.dialog, f"driver_image_{driver_id}", driver['image'])
            
            ttk.Label(scrollable_frame, text=f"{driver_name} ({driver_id})").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            
            # Points entry field
            self.point_vars[driver_id] = tk.StringVar(value="0.0")
            ttk.Entry(scrollable_frame, textvariable=self.point_vars[driver_id], width=10).grid(row=i, column=1, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save Points", command=self.save_points).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_points(self):
        """Process and save the entered points"""
        try:
            # Create results data
            results_data = []
            
            for driver_id, point_var in self.point_vars.items():
                try:
                    points = float(point_var.get())
                    results_data.append({
                        'RaceID': self.race_id,
                        'DriverID': driver_id,
                        'Points': points
                    })
                except ValueError:
                    messagebox.showerror("Error", f"Invalid point value for {driver_id}")
                    return
            
            # Call the callback with results
            if self.callback:
                success = self.callback(self.race_id, results_data)
                if success:
                    messagebox.showinfo("Success", f"Race results for {self.race_id} saved successfully!")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save race results")
            else:
                self.dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving points: {str(e)}")