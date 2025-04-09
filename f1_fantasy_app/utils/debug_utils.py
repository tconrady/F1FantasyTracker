"""
debug_utils.py - Simple debugging utility functions
"""

import logging
import traceback
import tkinter as tk
from tkinter import messagebox

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level to see all messages
    format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s',
    handlers=[
        logging.FileHandler('f1_fantasy_debug.log'),
        logging.StreamHandler()
    ]
)

debug_logger = logging.getLogger('f1_fantasy_debug')

def debug_trace(func):
    """Decorator to trace function calls with detailed logging"""
    def wrapper(*args, **kwargs):
        debug_logger.debug(f"ENTERING: {func.__name__}")
        debug_logger.debug(f"  ARGS: {args[1:] if len(args) > 0 and isinstance(args[0], object) else args}")
        debug_logger.debug(f"  KWARGS: {kwargs}")
        try:
            result = func(*args, **kwargs)
            debug_logger.debug(f"EXITING: {func.__name__} (success)")
            return result
        except Exception as e:
            debug_logger.error(f"EXCEPTION in {func.__name__}: {e}")
            debug_logger.error(traceback.format_exc())
            # Show error in UI
            messagebox.showerror("Debug Error", f"Error in {func.__name__}: {e}")
            raise
    return wrapper

def debug_print_structure(obj, prefix=""):
    """Print the structure of an object for debugging"""
    debug_logger.debug(f"{prefix}Object: {obj.__class__.__name__}")
    
    if hasattr(obj, '__dict__'):
        for key, value in obj.__dict__.items():
            if key.startswith('_'): continue  # Skip private attrs
            if callable(value): continue      # Skip methods
            debug_logger.debug(f"{prefix}  - {key}: {type(value)}")

def debug_popup(message):
    """Show a debug popup message"""
    messagebox.showinfo("Debug Info", message)
    debug_logger.debug(f"Debug popup: {message}")

def inspect_tkinter_widget(widget, prefix=""):
    """Inspect a Tkinter widget hierarchy"""
    if not widget:
        debug_logger.debug(f"{prefix}Widget is None")
        return
        
    debug_logger.debug(f"{prefix}Widget: {widget} ({widget.__class__.__name__})")
    
    # Check if it's a container that could have children
    if hasattr(widget, 'winfo_children'):
        children = widget.winfo_children()
        debug_logger.debug(f"{prefix}  - Children count: {len(children)}")
        for i, child in enumerate(children[:5]):  # Limit to first 5 to avoid huge logs
            inspect_tkinter_widget(child, prefix=f"{prefix}  Child {i}: ")
            
    # Check common widget properties
    if hasattr(widget, 'cget'):
        try:
            debug_logger.debug(f"{prefix}  - Text: {widget.cget('text')}")
        except:
            pass  # Not all widgets have text