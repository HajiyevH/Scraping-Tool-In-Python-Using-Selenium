import google.generativeai as genai
import os
from dotenv import load_dotenv
from src import database as db , config

# Load environment variables from .env
load_dotenv()


def format_postings(rows):
    """Format laptop rows for the LLM prompt."""
    postings = []
    for row in rows:
        postings.append(
            f"Name: {row.get('full_name', '')}\n"
            f"Price: {row.get('price', '')} {row.get('currency', '')}\n"
            f"Description: {row.get('description', '')}\n"
        )
    return "\n".join(postings)

def initalize_gemini(n: int = 1):
    """
    Analyze the first n laptops using Gemini and return the extracted specs for each.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    rows = db.get_first_n_rows(n)
    if not rows:
        return "No laptop data available for analysis."

    model = genai.GenerativeModel("gemini-2.0-flash")
    results = []
    for row in rows:
        prompt = config.PROMPT_TEMPLATE.format(
            full_name=row.get("full_name", ""),
            description=row.get("description", "")
        )
        response = model.generate_content(prompt)
        results.append({
            "link": row.get("link", ""),
            "extracted_specs": response.text
        })
    return results