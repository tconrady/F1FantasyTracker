"""
views/base_view.py - Base view class that other views will inherit from
"""

import tkinter as tk
from tkinter import ttk, messagebox

class BaseView:
    """Base view class for all views in the application"""
    
    def __init__(self, parent):
        """
        Initialize the base view.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
    def pack(self, **kwargs):
        """Pack the view's frame"""
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs):
        """Grid the view's frame"""
        self.frame.grid(**kwargs)
        
    def show(self):
        """Show the view"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide the view"""
        self.frame.pack_forget()
        
    def destroy(self):
        """Destroy the view"""
        self.frame.destroy()
        
    def show_message(self, title, message, message_type="info"):
        """Show a message dialog
        
        Args:
            title (str): Dialog title
            message (str): Message text
            message_type (str): One of "info", "error", "warning"
        """
        if message_type == "error":
            messagebox.showerror(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def show_confirmation(self, title, message):
        """Show a confirmation dialog
        
        Args:
            title (str): Dialog title
            message (str): Message text
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        return messagebox.askyesno(title, message)