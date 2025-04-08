"""
utils/scraper.py - Functions for scraping race results
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import pandas as pd

logger = logging.getLogger(__name__)

def initialize_webdriver(headless=True):
    """
    Initialize a WebDriver for scraping.
    
    Args:
        headless (bool): Whether to run in headless mode
        
    Returns:
        WebDriver: Initialized WebDriver or None if failed
    """
    try:
        # Install or update ChromeDriver
        chromedriver_autoinstaller.install()
        
        # Configure WebDriver options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Create WebDriver
        driver = webdriver.Chrome(options=options)
        logger.info("WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        return None

def get_driver_id_by_name(driver_name, driver_mapping):
    """
    Get driver ID from name with improved name matching.
    
    Args:
        driver_name (str): Driver name from website (first and last name)
        driver_mapping (dict): Dictionary mapping driver names to driver IDs
        
    Returns:
        str: Driver ID or None if not found
    """
    try:
        # Normalize the input name
        driver_name = driver_name.lower().strip()
        
        # Check exact match
        if driver_name in driver_mapping:
            return driver_mapping[driver_name]
        
        # Handle specific cases
        if driver_name == "kimi antonelli" or driver_name == "andrea kimi antonelli":
            return "ANT"
        
        # Try partial matches
        parts = driver_name.split()
        if len(parts) > 1:
            # Try matching on first name + last name
            for known_name, driver_id in driver_mapping.items():
                known_parts = known_name.split()
                if any(part in known_parts for part in parts):
                    # At least one part of the name matches
                    return driver_id
        
        logger.warning(f"Driver '{driver_name}' not found in mapping")
        return None
    except Exception as e:
        logger.error(f"Error mapping driver name to ID: {e}")
        return None

def scrape_race_results(race_id):
    """
    Scrape fantasy points for a specific race.
    
    Args:
        race_id (str): Race ID to scrape
        
    Returns:
        list: List of driver result dictionaries or empty list if failed
    """
    logger.info(f"Scraping fantasy points for race {race_id}...")
    
    # Driver name to ID mapping
    driver_mapping = {
        'andrea kimi antonelli': 'ANT',
        'kimi antonelli': 'ANT',
        'gabriel bortoleto': 'BOR',
        'isack hadjar': 'HAD',
        'jack doohan': 'DOO',
        'max verstappen': 'VER',
        'lewis hamilton': 'HAM',
        'lando norris': 'NOR',
        'charles leclerc': 'LEC',
        'carlos sainz': 'SAI',
        'oscar piastri': 'PIA',
        'george russell': 'RUS',
        'liam lawson': 'LAW',
        'fernando alonso': 'ALO',
        'lance stroll': 'STR',
        'pierre gasly': 'GAS',
        'esteban ocon': 'OCO',
        'alexander albon': 'ALB',
        'yuki tsunoda': 'TSU',
        'oliver bearman': 'BEA',
        'nico hulkenberg': 'HUL'
    }
    
    # Initialize WebDriver
    driver = initialize_webdriver()
    if not driver:
        return []
    
    try:
        # Go to the F1 Fantasy detailed statistics page
        driver.get('https://fantasy.formula1.com/en/statistics/details?tab=driver&filter=fPoints')
        
        # Wait for the driver statistics list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.si-stats__list-grid"))
        )
        
        # Parse the data from the page
        drivers_data = []
        
        # Find all driver rows
        driver_elements = driver.find_elements(By.CSS_SELECTOR, 'div.si-stats__list-grid > ul > li:not(:first-child)')
        logger.info(f"Found {len(driver_elements)} driver elements")
        
        for driver_element in driver_elements:
            try:
                # Extract driver name (first and last name spans)
                name_spans = driver_element.find_elements(By.CSS_SELECTOR, 'div.si-miniCard__name > span')
                if len(name_spans) >= 2:
                    first_name = name_spans[0].text.strip()
                    last_name = name_spans[1].text.strip()
                    full_name = f"{first_name} {last_name}".title()  # Proper case
                else:
                    # Fallback if the structure is different
                    full_name = ' '.join([span.text for span in name_spans]).title()
                
                # Extract points
                points_element = driver_element.find_element(By.CSS_SELECTOR, 'div.si-stats__list-item.statvalue div.si-stats__list-value')
                points_text = points_element.text.strip()
                
                # Get driver ID based on name
                driver_id = get_driver_id_by_name(full_name.lower(), driver_mapping)
                
                # Only add if we found a valid driver ID
                if driver_id:
                    # Convert points to float, handle empty or non-numeric values
                    try:
                        points = float(points_text)
                    except ValueError:
                        points = 0.0
                        
                    drivers_data.append({
                        'RaceID': race_id,
                        'DriverID': driver_id,
                        'Points': points
                    })
                    logger.info(f"Scraped data for {full_name} ({driver_id}): {points} points")
                else:
                    logger.warning(f"Could not find driver ID for {full_name}")
                    
            except Exception as e:
                logger.error(f"Error processing driver element: {e}")
                continue
                
        driver.quit()
        
        if not drivers_data:
            logger.warning(f"No driver data scraped for race {race_id}")
            
        return drivers_data
    except Exception as e:
        logger.error(f"Error scraping fantasy points: {e}")
        if driver:
            driver.quit()
        return []