Tap.az Data Scraper

Instructions:
1. Make sure you have Google Chrome installed.
2. No need to install Chromedriver separately — it is included.
3. Install Python packages using:
    pip install -r requirements.txt

Note:
- If Chrome version mismatch happens, download matching Chromedriver from https://chromedriver.chromium.org/downloads

Roadmap :

✅ PHASED PLAN (Efficient 10–15 Hour Build)

🧱 Phase 1: Convert Scraper into a Clean Function

Goal: Make your scraper reusable and modular.
	1.	✅ Wrap your scraping logic in a function like def scrape_new_laptops(limit=100)
	2.	✅ Change it to return a list of dictionaries (laptop listings)
	3.	✅ Make it skip links already seen using a SQLite table scraped_links

→ Estimated Time: 2–3 hours

⸻

📦 Phase 2: Add SQLite Storage

Goal: Save all listings in a local database.
	1.	✅ Create SQLite tables:
	•	laptops (title, price, specs, date, url, type, desc, scraped_at)
	•	scraped_links (url)
	2.	✅ Each time you scrape, insert only if url not in scraped_links
	3.	✅ Test saving 50–100 listings

→ Estimated Time: 2 hours

⸻

🌐 Phase 3: FastAPI Backend

Goal: Expose your logic via an API
	1.	✅ GET /scrape → Triggers scraper and returns newly added listings
	2.	✅ GET /recent → Returns latest 100 entries from DB
	3.	✅ POST /analyze → Sends latest 100 to GPT/Gemini and returns best 3 deals

→ Estimated Time: 3 hours

⸻

⏲️ Phase 4: Automation

Goal: Automatically keep data fresh
	1.	✅ Use APScheduler in FastAPI to call scrape_new_laptops(limit=100) every 60 minutes
	2.	OR set up a cron job that runs python scrape.py every hour

→ Estimated Time: 1 hour

⸻

🧠 Phase 5: GPT/Gemini Integration

Goal: Analyze best-value deals using AI
	1.	✅ Format recent listings into a prompt
	2.	✅ Call GPT or Gemini via their API
	3.	✅ Return ranked list of 3–5 best deals and short reasoning

→ Estimated Time: 2 hours

⸻

📱 (Optional) Phase 6: SwiftUI Frontend

Goal: Build a basic iOS UI that calls your FastAPI endpoints
	1.	✅ Display latest deals (GET /recent)
	2.	✅ Show best deals (GET /analyze)
	3.	✅ (Optional) Refresh or search features

→ Estimated Time: 4–6 hours (if you’re learning SwiftUI)

⸻

🧠 Extra Tips
	•	Start with console testing before wiring into FastAPI.
	•	Keep your scraper limit configurable (e.g., 50 items).
	•	Cache AI results for each scrape in a table like ai_analysis.

⸻

Would you like:
	•	A project folder structure suggestion?
	•	SQLite schema or example DB helper code?
	•	Prompt formatting code for OpenAI/Gemini?

Let me know what you’d like help with next.