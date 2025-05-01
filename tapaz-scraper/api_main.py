from typing import Union , Optional,List,Dict,Any
from fastapi import FastAPI, HTTPException
import asyncio
import src.database as db
from src import scraper,utils,config
from fastapi.responses import StreamingResponse
import io
import pandas as pd

app = FastAPI()

db.init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/data/{limit}")
def read_item(limit : int):
    return db.get_recent_laptops(limit)



@app.get("/recent", response_model=List[Dict[str, Any]])
async def get_data_with_date(limit: int = 100, since_date: Optional[str] = None):
    print(f"API Endpoint /recent received: limit={limit}, since_date='{since_date}' (Type: {type(since_date)})")
    loop = asyncio.get_event_loop()
    rows = await loop.run_in_executor(None, db.get_recent_laptops, limit, since_date)
    return rows

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

@app.get("/export")
async def export_data(
    format: str = "csv",
    limit: int = 1000,
    since_date: Optional[str] = None
):
    """
    Export laptops data as CSV or XLSX, with optional filters.
    """
    loop = asyncio.get_event_loop()
    rows = await loop.run_in_executor(None, db.get_recent_laptops, limit, since_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No data to export.")

    df = pd.DataFrame(rows)
    if format == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=laptops.xlsx"}
        )
    elif format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=laptops.csv"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'xlsx'.")
