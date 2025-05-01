from typing import Union , Optional,List,Dict,Any
from fastapi import FastAPI, HTTPException
import asyncio
import src.database as db
from src import scraper,utils,config

app = FastAPI()

db.init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/{limit}")
def read_item(limit : int):
    return db.get_recent_laptops(limit)

@app.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_data(limit: int = 100, since_date: Optional[str] = None):
    print(f"API Endpoint /recent received: limit={limit}, since_date='{since_date}' (Type: {type(since_date)})")

    return db.get_recent_laptops(limit=limit , since_date=since_date)


@app.post("/scrape", response_model=List[Dict[str, Any]])
async def trigger_scrape():
    """
    Triggers the scraping process and returns the newly scraped elements.
    """
    loop = asyncio.get_event_loop()
    driver = None
    try:
        # Initialize WebDriver in executor
        driver = await loop.run_in_executor(None, scraper.initialize_driver)
        if not driver:
            raise HTTPException(status_code=500, detail="Failed to initialize WebDriver")
        # Run the scraper in executor
        scraped_data = await loop.run_in_executor(
            None,
            scraper.scrape_tapaz_laptops,
            driver,
            config.BASE_URL,
            config.MAX_ITEMS_TO_SCRAPE
        )
        # Save the scraped data
        utils.save_data(scraped_data)
        # Return the scraped elements as a list of dicts
        keys = scraped_data.keys()
        num_items = len(scraped_data.get("link", []))
        result = [dict(zip(keys, [scraped_data[k][i] for k in keys])) for i in range(num_items)]
        return result
    except Exception as e:
        print(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if driver:
            driver.quit()
