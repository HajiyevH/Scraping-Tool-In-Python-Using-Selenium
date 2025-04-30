# filepath: tapaz-scraper/src/main.py
from src import scraper
from src import utils
from src import config # Good practice to import config if needed directly here too

def main():
    """Main execution function."""
    driver = None # Initialize driver to None
    try:
        driver = scraper.initialize_driver()
        if driver:
            scraped_data = scraper.scrape_tapaz_laptops(driver, max_items=config.MAX_ITEMS_TO_SCRAPE)
            utils.save_data(scraped_data)
        else:
            print("Failed to initialize WebDriver. Exiting.")
    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit() # Use quit() instead of close() to end the session and close all windows

if __name__ == "__main__":
    # This block runs only when the script is executed directly
    main()