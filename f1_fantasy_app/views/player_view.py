"""
views/player_view.py - View for player management
"""

import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView

class PlayerView(BaseView):
    """View for player management"""
    
    def __init__(self, parent):
        """
        Initialize the player view.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        
        # Split into left and right frames
        self.left_frame = ttk.Frame(self.frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_frame = ttk.Frame(self.frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set up the left frame (add player form)
        self.setup_add_player_form()
        
        # Set up the right frame (player list)
        self.setup_player_list()
        
    def setup_add_player_form(self):
        """Set up the form for adding a new player"""
        add_player_frame = ttk.LabelFrame(self.left_frame, text="Add New Player")
        add_player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Player ID
        ttk.Label(add_player_frame, text="Player ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_id_var = tk.StringVar()
        ttk.Entry(add_player_frame, textvariable=self.player_id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Player name
        ttk.Label(add_player_frame, text="Player Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_name_var = tk.StringVar()
        ttk.Entry(add_player_frame, textvariable=self.player_name_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # First driver
        ttk.Label(add_player_frame, text="First Driver:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.driver1_var = tk.StringVar()
        self.driver1_dropdown = ttk.Combobox(add_player_frame, textvariable=self.driver1_var, state="readonly")
        self.driver1_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # First driver image placeholder
        self.driver1_image_label = ttk.Label(add_player_frame)
        self.driver1_image_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Second driver
        ttk.Label(add_player_frame, text="Second Driver:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.driver2_var = tk.StringVar()
        self.driver2_dropdown = ttk.Combobox(add_player_frame, textvariable=self.driver2_var, state="readonly")
        self.driver2_dropdown.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Second driver image placeholder
        self.driver2_image_label = ttk.Label(add_player_frame)
        self.driver2_image_label.grid(row=3, column=2, padx=5, pady=5)
        
        # Add button
        ttk.Button(add_player_frame, text="Add Player", command=self.on_add_player).grid(row=4, column=0, columnspan=3, padx=5, pady=10)
        
        # Credit calculator frame
        credit_frame = ttk.LabelFrame(self.left_frame, text="Credit Calculator")
        credit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(credit_frame, text="Current Selection:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.credit_info_var = tk.StringVar()
        self.credit_info_var.set("Select two drivers to see credit total")
        ttk.Label(credit_frame, textvariable=self.credit_info_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Team preview frame
        preview_frame = ttk.LabelFrame(self.left_frame, text="Selected Team Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for team preview
        self.preview_canvas = tk.Canvas(preview_frame, bg="white")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_player_list(self):
        """Set up the player list treeview"""
        player_list_frame = ttk.LabelFrame(self.right_frame, text="Current Players")
        player_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for players
        columns = ("PlayerID", "PlayerName", "Drivers", "Credits")
        self.player_tree = ttk.Treeview(player_list_frame, columns=columns, show="headings")
        
        # Set column headings
        self.player_tree.heading("PlayerID", text="ID")
        self.player_tree.heading("PlayerName", text="Name")
        self.player_tree.heading("Drivers", text="Drivers")
        self.player_tree.heading("Credits", text="Credits")
        
        # Set column widths
        self.player_tree.column("PlayerID", width=50)
        self.player_tree.column("PlayerName", width=100)
        self.player_tree.column("Drivers", width=250)
        self.player_tree.column("Credits", width=60)
        
        # Add a scrollbar
        player_scrollbar = ttk.Scrollbar(player_list_frame, orient=tk.VERTICAL, command=self.player_tree.yview)
        self.player_tree.configure(yscrollcommand=player_scrollbar.set)
        
        self.player_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        player_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.player_tree.bind("<<TreeviewSelect>>", self.on_player_selected)
        
        # Add buttons
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Refresh Players", command=self.on_refresh_players).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Change Driver", command=self.on_change_driver).pack(side=tk.LEFT, padx=5)
        
    def set_driver_options(self, driver_options):
        """Set the options for driver dropdowns
        
        Args:
            driver_options (list): List of driver option strings
        """
        self.driver1_dropdown['values'] = driver_options
        self.driver2_dropdown['values'] = driver_options
        
    def update_player_list(self, players_data):
        """Update the player list with new data
        
        Args:
            players_data (list): List of player data tuples (id, name, drivers, credits)
        """
        # Clear existing items
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)
        
        # Add new items
        for player_data in players_data:
            self.player_tree.insert('', tk.END, values=player_data)
            
    def update_credit_info(self, credit_info):
        """Update the credit information
        
        Args:
            credit_info (str): Credit information text
        """
        self.credit_info_var.set(credit_info)
        
    def update_driver1_image(self, image):
        """Update the first driver image
        
        Args:
            image: PhotoImage object or None
        """
        if image:
            self.driver1_image_label.configure(image=image)
            self.driver1_image = image  # Keep a reference
        else:
            self.driver1_image_label.configure(image='')
            
    def update_driver2_image(self, image):
        """Update the second driver image
        
        Args:
            image: PhotoImage object or None
        """
        if image:
            self.driver2_image_label.configure(image=image)
            self.driver2_image = image  # Keep a reference
        else:
            self.driver2_image_label.configure(image='')
    
    def update_team_preview(self, driver1_id, driver2_id, driver1_image, driver2_image, driver1_name, driver2_name, driver1_credits, driver2_credits, team1_logo, team2_logo):
        """Update the team preview canvas
        
        Args:
            driver1_id (str): First driver ID
            driver2_id (str): Second driver ID
            driver1_image: First driver image
            driver2_image: Second driver image
            driver1_name (str): First driver name
            driver2_name (str): Second driver name
            driver1_credits (float): First driver credits
            driver2_credits (float): Second driver credits
            team1_logo: First team logo
            team2_logo: Second team logo
        """
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Set up display
        image_size = (100, 100)
        padding = 20
        
        # Calculate positions
        center_x = self.preview_canvas.winfo_width() // 2
        if center_x < 50:
            center_x = 200  # Default if canvas not yet sized
        
        # Display first driver
        if driver1_image:
            x1 = center_x - image_size[0] - padding
            self.preview_canvas.create_image(x1, padding, image=driver1_image, anchor=tk.NW)
            self.preview_driver1_image = driver1_image  # Keep a reference
            
            # Driver name
            self.preview_canvas.create_text(
                x1 + image_size[0] // 2, padding + image_size[1] + 5,
                text=f"{driver1_name} ({driver1_id})",
                anchor=tk.N,
                font=("Arial", 10, "bold")
            )
            
            # Team logo
            if team1_logo:
                self.preview_canvas.create_image(
                    x1 + image_size[0] // 2 - 30, padding + image_size[1] + 30,
                    image=team1_logo, anchor=tk.NW
                )
                self.preview_team1_logo = team1_logo  # Keep a reference
        
        # Display second driver
        if driver2_image:
            x2 = center_x + padding
            self.preview_canvas.create_image(x2, padding, image=driver2_image, anchor=tk.NW)
            self.preview_driver2_image = driver2_image  # Keep a reference
            
            # Driver name
            self.preview_canvas.create_text(
                x2 + image_size[0] // 2, padding + image_size[1] + 5,
                text=f"{driver2_name} ({driver2_id})",
                anchor=tk.N,
                font=("Arial", 10, "bold")
            )
            
            # Team logo
            if team2_logo:
                self.preview_canvas.create_image(
                    x2 + image_size[0] // 2 - 30, padding + image_size[1] + 30,
                    image=team2_logo, anchor=tk.NW
                )
                self.preview_team2_logo = team2_logo  # Keep a reference
        
        # Display total credits
        total_credits = driver1_credits + driver2_credits
        
        self.preview_canvas.create_text(
            center_x, padding * 2 + image_size[1] + 60,
            text=f"Total Credits: {total_credits}/5",
            anchor=tk.N,
            font=("Arial", 12, "bold"),
            fill="green" if total_credits <= 5 else "red"
        )
    
    def get_selected_player(self):
        """Get the selected player from the treeview
        
        Returns:
            tuple: (player_id, player_name) or (None, None) if no selection
        """
        selected_item = self.player_tree.selection()
        if not selected_item:
            return None, None
        
        player_id = self.player_tree.item(selected_item[0], 'values')[0]
        player_name = self.player_tree.item(selected_item[0], 'values')[1]
        return player_id, player_name
    
    def get_form_data(self):
        """Get the data from the add player form
        
        Returns:
            tuple: (player_id, player_name, driver1_id, driver2_id)
        """
        player_id = self.player_id_var.get().strip()
        player_name = self.player_name_var.get().strip()
        
        driver1 = self.driver1_var.get()
        driver2 = self.driver2_var.get()
        
        # Extract driver IDs
        driver1_id = driver1.split('(')[1].split(')')[0] if '(' in driver1 and ')' in driver1 else ""
        driver2_id = driver2.split('(')[1].split(')')[0] if '(' in driver2 and ')' in driver2 else ""
        
        return player_id, player_name, driver1_id, driver2_id
    
    def clear_form(self):
        """Clear the add player form"""
        self.player_id_var.set("")
        self.player_name_var.set("")
        self.driver1_var.set("")
        self.driver2_var.set("")
        self.update_driver1_image(None)
        self.update_driver2_image(None)
        self.preview_canvas.delete("all")
    
    # Event handlers - to be overridden by controller
    def on_add_player(self):
        """Handle add player button click"""
        pass
    
    def on_refresh_players(self):
        """Handle refresh players button click"""
        pass
    
    def on_change_driver(self):
        """Handle change driver button click"""
        pass
    
    def on_player_selected(self, event):
        """Handle player selection in treeview"""
        pass