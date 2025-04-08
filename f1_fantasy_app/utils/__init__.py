"""
utils/__init__.py - Utility functions for the F1 Fantasy application
"""

from utils.excel import (
    is_file_accessible, 
    create_excel_if_not_exists, 
    backup_excel_file,
    save_dataframe_to_excel,
    read_sheet_from_excel
)

from utils.scraper import (
    initialize_webdriver,
    get_driver_id_by_name,
    scrape_race_results
)