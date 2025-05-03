import google.generativeai as genai
import os
from dotenv import load_dotenv
from src import database as db , config,scraper
import json
import re
load_dotenv()
def clean_llm_response(text):
    """
    Removes markdown code fences and trims whitespace from LLM response.
    """
    if not text:
        return ""
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return cleaned.strip()

def extract_specs_from_llm(row):
    """
    Given a row (dict), sends prompt to Gemini and returns a dict with extracted specs.
    """
    prompt = config.PROMPT_TEMPLATE.format(
        full_name=row.get("full_name", ""),
        description=row.get("description", "")
    )
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    try:
        specs = json.loads(response.text)
    except Exception as e:
        print(f"Failed to parse LLM response for {row.get('link', '')}: {e}")
        specs = {}
    # Merge original row with new specs (specs overwrite existing keys if any)
    new_row = {**row, **specs}
    return new_row

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

def clean_llm_response(text):
    """
    Removes markdown code fences and trims whitespace from LLM response.
    """
    if not text:
        return ""
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return cleaned.strip()
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
        cleaned = clean_llm_response(response.text)
        try:
            specs = json.loads(cleaned)
            db.update_row_with_llm_specs(row.get("link", ""), specs)
            results.append({
                "link": row.get("link", ""),
                "extracted_specs": cleaned
            })
        except Exception as e:
            print(f"Failed to parse or update specs for {row.get('link', '')}: {e}")
    return results