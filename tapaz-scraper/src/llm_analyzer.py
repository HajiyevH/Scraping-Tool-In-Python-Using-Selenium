import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
def initalize_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say hello to the world! Like you are Eyyub Yaqubov")
    print(response.text)