"""
utils/scraper.py - Functions for scraping F1 Fantasy data
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import pandas as pd
from datetime import datetime

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
        
        # Handle specific capitalization from the website
        if driver_name == "kimi antonelli" or driver_name == "andrea kimi antonelli":
            driver_name = "andrea kimi antonelli"
        
        # Try exact match first
        if driver_name in driver_mapping:
            return driver_mapping[driver_name]
            
        # Try partial matches
        parts = driver_name.split()
        if len(parts) > 1:
            # Try matching on first name + last name
            for known_name, driver_id in driver_mapping.items():
                known_parts = known_name.split()
                if any(part in known_parts for part in parts):
                    # At least one part of the name matches
                    return driver_id
        
        # Special case handling for name parts
        for known_name, driver_id in driver_mapping.items():
            known_parts = known_name.split()
            driver_parts = driver_name.split()
            
            # Match if first name matches and last name is contained (might be capitalized)
            if len(known_parts) > 0 and len(driver_parts) > 0:
                if known_parts[0] == driver_parts[0]:  # First name matches
                    return driver_id
        
        logger.warning(f"Driver '{driver_name}' not found in mapping")
        return None
    except Exception as e:
        logger.error(f"Error mapping driver name to ID: {e}")
        return None

def get_default_driver_mapping():
    """
    Get the default driver name to ID mapping.
    
    Returns:
        dict: Dictionary mapping normalized driver names to IDs
    """
    return {
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

def scrape_race_results(race_id, url='https://fantasy.formula1.com/en/statistics/details?tab=driver&filter=fPoints', 
                        driver_mapping=None):
    """
    Scrape fantasy points for a specific race.
    
    Args:
        race_id (str): Race ID to scrape
        url (str): URL to scrape points from
        driver_mapping (dict, optional): Mapping of driver names to IDs
        
    Returns:
        list: List of driver result dictionaries or empty list if failed
    """
    logger.info(f"Scraping fantasy points for race {race_id} from {url}")
    
    # Use default mapping if none provided
    if driver_mapping is None:
        driver_mapping = get_default_driver_mapping()
    
    # Initialize WebDriver
    driver = initialize_webdriver()
    if not driver:
        logger.error("Failed to initialize WebDriver")
        return []
    
    try:
        # Go to the F1 Fantasy statistics page
        driver.get(url)
        
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
                
                # Extract points - directly from the points column
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

def scrape_driver_standings(url='https://fantasy.formula1.com/en/statistics/details?tab=driver'):
    """
    Scrape the current driver standings.
    
    Args:
        url (str): URL to scrape standings from
        
    Returns:
        list: List of driver standings dictionaries or empty list if failed
    """
    logger.info(f"Scraping driver standings from {url}")
    
    # Initialize WebDriver
    driver = initialize_webdriver()
    if not driver:
        return []
    
    try:
        # Go to the F1 Fantasy statistics page
        driver.get(url)
        
        # Wait for the driver statistics list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.si-stats__list-grid"))
        )
        
        # Parse the data from the page
        standings_data = []
        
        # Find all driver rows
        driver_elements = driver.find_elements(By.CSS_SELECTOR, 'div.si-stats__list-grid > ul > li:not(:first-child)')
        logger.info(f"Found {len(driver_elements)} driver elements in standings")
        
        position = 1
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
                driver_id = get_driver_id_by_name(full_name.lower(), get_default_driver_mapping())
                
                if driver_id:
                    # Convert points to float
                    try:
                        points = float(points_text)
                    except ValueError:
                        points = 0.0
                        
                    standings_data.append({
                        'Position': position,
                        'DriverID': driver_id,
                        'Name': full_name,
                        'Points': points
                    })
                    
                    position += 1
                    
            except Exception as e:
                logger.error(f"Error processing driver standing element: {e}")
                continue
                
        driver.quit()
        
        return standings_data
    except Exception as e:
        logger.error(f"Error scraping driver standings: {e}")
        if driver:
            driver.quit()
        return []

def update_with_scraper(race_id, data_manager):
    """
    Update race results by scraping the website and updating the data manager.
    
    Args:
        race_id (str): Race ID to update
        data_manager: Data manager instance to update with scraped data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Scrape race results
        results = scrape_race_results(race_id)
        if not results:
            logger.error(f"Failed to scrape results for race {race_id}")
            return False
        
        # Save results to data manager
        if not data_manager.save_race_results(race_id, results):
            logger.error(f"Failed to save scraped results for race {race_id}")
            return False
        
        # Calculate player points
        if not data_manager.calculate_player_points_for_race(race_id):
            logger.error(f"Failed to calculate player points for race {race_id}")
            return False
        
        # Update race status to completed
        logger.info(f"Successfully updated race results for {race_id}")
        return True
    except Exception as e:
        logger.error(f"Error in update_with_scraper: {e}")
        return False