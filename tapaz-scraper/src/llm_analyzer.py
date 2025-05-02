import google.generativeai as genai
import os
from dotenv import load_dotenv
from src import database as db

# Load environment variables from .env
load_dotenv()

# Prompt template for ranking laptops
PROMPT_TEMPLATE = """
You are an expert in evaluating second-hand laptops for price and performance. Here is a list of laptop postings, each with a name, price, and description:

{POSTINGS}

Please do the following:
1. Rank these laptops from best to worst based on price/performance ratio, considering both the price and the specifications/features in the description.
2. For the top 3 laptops, explain in 1-2 sentences why you ranked them highest.
3. Only output the ranking (with names and prices) and the explanations for the top 3. Do not include any other commentary.

Format your answer as:

Ranking:
1. [Laptop Name] - [Price]
2. [Laptop Name] - [Price]
3. [Laptop Name] - [Price]
...

Explanations:
1. [Explanation for #1]
2. [Explanation for #2]
3. [Explanation for #3]
"""

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

def initalize_gemini(n: int = 3):
    """
    Analyze the first n laptops using Gemini and return the ranking and explanations.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    rows = db.get_first_n_rows(n)
    if not rows:
        return "No laptop data available for analysis."
    prompt = PROMPT_TEMPLATE.format(POSTINGS=format_postings(rows))
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text