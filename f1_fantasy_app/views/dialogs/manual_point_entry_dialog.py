"""
views/dialogs/manual_point_entry_dialog.py - Dialog for manual entry of driver points
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ManualPointEntryDialog:
    """Dialog for manual entry of driver points for a race"""
    
    def __init__(self, parent, race_id, race_name, drivers_data, image_loader, on_save=None):
        """
        Initialize the manual point entry dialog.
        
        Args:
            parent: The parent widget
            race_id (str): Race ID
            race_name (str): Race name
            drivers_data (pd.DataFrame): DataFrame containing driver data
            image_loader: The image loader instance for driver images
            on_save (callable, optional): Function to call when points are saved
        """
        self.parent = parent
        self.race_id = race_id
        self.race_name = race_name
        self.drivers_data = drivers_data
        self.image_loader = image_loader
        self.on_save = on_save
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Manual Point Entry for {race_id} - {race_name}")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create dialog elements
        self._create_widgets()
        
        # Store references to images to prevent garbage collection
        self.images = {}
    
    def _create_widgets(self):
        """Create all dialog widgets"""
        # Title label
        ttk.Label(self.dialog, text=f"Enter fantasy points for each driver for {self.race_id} - {self.race_name}").pack(pady=10)
        
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
        self.point_vars = {}
        
        ttk.Label(scrollable_frame, text="Driver").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Points").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="").grid(row=0, column=2, padx=5, pady=5)  # For images
        
        for i, (_, driver) in enumerate(self.drivers_data.iterrows(), 1):
            driver_id = driver['DriverID']
            driver_name = driver['Name']
            
            # Driver image
            driver_image = self.image_loader.get_driver_image(driver_id, (30, 30))
            if driver_image:
                image_label = ttk.Label(scrollable_frame, image=driver_image)
                image_label.grid(row=i, column=2, padx=5, pady=2)
                # Store reference to prevent garbage collection
                self.images[f"driver_{driver_id}"] = driver_image
            else:
                # Create placeholder if image not found
                placeholder = self.image_loader.create_placeholder_image(driver_id, (30, 30))
                image_label = ttk.Label(scrollable_frame, image=placeholder)
                image_label.grid(row=i, column=2, padx=5, pady=2)
                # Store reference to prevent garbage collection
                self.images[f"driver_{driver_id}"] = placeholder
            
            ttk.Label(scrollable_frame, text=f"{driver_name} ({driver_id})").grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            
            point_var = tk.StringVar(value="0.0")
            self.point_vars[driver_id] = point_var
            
            ttk.Entry(scrollable_frame, textvariable=point_var, width=10).grid(row=i, column=1, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        ttk.Button(button_frame, text="Save Points", command=self._on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _on_save(self):
        """Handle save points button click"""
        try:
            # Create result data
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
            
            # Call save function if provided
            if self.on_save:
                self.on_save(self.race_id, results_data)
            
            # Close dialog
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving points: {e}")