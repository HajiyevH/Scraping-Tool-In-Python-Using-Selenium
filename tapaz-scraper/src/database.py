import sqlite3
from . import config
import os
from typing import Optional, List, Dict, Any 

def init_db():
    """Initializes the database and creates the 'laptops' table if it doesn't exist."""
    # Ensure the output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        # Create table - Adjust column names and types as needed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS laptops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT,
                date TEXT,
                link TEXT UNIQUE, -- Ensure links are unique to avoid duplicates
                price REAL,       -- Use REAL for potential decimal prices
                comp_name TEXT,
                full_name TEXT,
                currency TEXT,
                description TEXT,
                type TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Track when it was scraped
            )
        ''')
        conn.commit()
        print(f"Database initialized successfully at {config.DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Database error during initialization:a {e}")
    finally:
        if conn:
            conn.close()

def insert_data(data_dict):
    """Inserts scraped data from a dictionary into the SQLite database."""
    if not data_dict or not any(data_dict.values()):
        print("No data provided to insert into the database.")
        return

    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()

        # Prepare data for insertion (list of tuples)
        # Assumes all lists in data_dict have the same length
        num_items = len(data_dict.get("link", []))
        if num_items == 0:
            print("Data dictionary is empty or missing 'link' key.")
            return

        rows_to_insert = []
        keys = ["location", "date", "link", "price", "comp_name", "full_name", "currency", "description", "type"]

        for i in range(num_items):
            row = tuple(data_dict.get(key, [])[i] if i < len(data_dict.get(key, [])) else None for key in keys)
             # Basic price cleaning (remove non-numeric, convert to float)
            price_str = str(data_dict.get("price", [])[i]).replace(' ', '').replace('AZN', '').replace(',', '.') if i < len(data_dict.get("price", [])) else '0'
            try:
                price_float = float(price_str)
            except ValueError:
                price_float = None # Or 0.0, depending on how you want to handle invalid prices

            row_list = list(row)
            price_index = keys.index("price")
            row_list[price_index] = price_float # Replace original price string with float
            rows_to_insert.append(tuple(row_list))


        # Use INSERT OR IGNORE to skip inserting if a link already exists (due to UNIQUE constraint)
        sql = '''
            INSERT OR IGNORE INTO laptops (location, date, link, price, comp_name, full_name, currency, description, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        cursor.executemany(sql, rows_to_insert)
        conn.commit()
        inserted_count = cursor.rowcount
        print(f"Attempted to insert {len(rows_to_insert)} rows. Successfully inserted {inserted_count} new rows.")

    except sqlite3.Error as e:
        print(f"Database error during insertion: {e}")
    except IndexError as e:
         print(f"Data alignment error: Check if all lists in data_dict have the same length. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")
    finally:
        if conn:
            conn.close()

def get_recent_laptops(limit: int = 100, since_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches the most recent 'limit' number of laptop entries from the database.

    Args:
        limit (int): The maximum number of laptops to retrieve. Defaults to 100.

    Returns:
        list: A list of dictionaries, where each dictionary represents a laptop row.
              Returns an empty list if no data is found or an error occurs.
    """
    conn = None
    laptops = []
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        params = []
        query = "SELECT * FROM laptops"

        # Add WHERE clause if since_id is provided and valid
        valid_since_date = None
        if since_date:
            try:
                # Validate the format 'YYYY-MM-DD'
                datetime.strptime(since_date, '%Y-%m-%d')
                valid_since_date = since_date # Use it if format is correct
            except (ValueError, TypeError):
                print(f"Warning: Invalid since_date format provided ('{since_date}'). Expected 'YYYY-MM-DD'. Ignoring filter.")

        if valid_since_date:
            query += " WHERE date > ?" # Use >= to include the date itself
            params.append(valid_since_date)
        # Add ORDER BY and LIMIT
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        print(f"Executing query: {query} with params: {tuple(params)}") # Debug print
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        # Convert sqlite3.Row objects to standard dictionaries
        laptops = [dict(row) for row in rows]
        print(f"Successfully fetched {len(laptops)} recent laptops.")

    except sqlite3.Error as e:
        print(f"Database error while fetching recent laptops: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching recent laptops: {e}")
    finally:
        if conn:
            conn.close()
    return laptops    

def is_link_in_database(href: str) -> bool:
    """Checks if a given link already exists in the laptops table."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM laptops WHERE link = ? LIMIT 1", (href,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"Database error while checking link in laptops: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while checking link in laptops: {e}")
    finally:
        if conn:
            conn.close()
    return False