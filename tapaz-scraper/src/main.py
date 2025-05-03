from src import scraper
from src import utils
from src import config
from src import database 
from src import llm_analyzer

def main():
    """Main execution function."""
    driver = None # Initialize driver to None
    try:
        # --- Initialize Database ---
        print("Initializing database...")
        database.init_db() # Create DB and table if they don't exist

        # --- Initialize WebDriver ---
        print("Initializing WebDriver...")
        driver = scraper.initialize_driver()
        if driver:
            print("Starting scraping process...")
            scraped_data = scraper.scrape_tapaz_laptops(driver, max_items=config.MAX_ITEMS_TO_SCRAPE)
            print("Scraping finished. Saving data...")
            utils.save_data(scraped_data)
            print("Data saving process complete.")
        else:
            print("Failed to initialize WebDriver. Exiting.")
    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if driver:
            print("Closing WebDriver.")
            driver.quit() # Use quit() instead of close() to end the session

if __name__ == "__main__":
    # main()
    # llm_analyzer.initalize_gemini()
    # print(scraper.scrape_product_details(scraper.initialize_driver(),"https://tap.az/elanlar/elektronika/noutbuklar/44082314"))
    main()