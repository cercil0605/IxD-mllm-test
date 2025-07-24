
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

def analyze_room_condition(image_path, prompt_path):
    """
    Analyzes the condition of a room from an image based on a given prompt.

    Args:
        image_path (str): The path to the image file.
        prompt_path (str): The path to the text file containing the prompt.

    Returns:
        dict: A dictionary containing the analysis results from the Gemini API.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY is not set. Please check your .env file.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')

    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    uploaded_file = genai.upload_file(path=image_path)

    response = model.generate_content([prompt_text, uploaded_file])

    # Clean up the response text
    text = response.text
    text = text.strip().replace('```json', '').replace('```', '').strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response text: {response.text}")
        return None
