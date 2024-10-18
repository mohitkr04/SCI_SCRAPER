import os
import google.generativeai as genai
import base64
import requests
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv() 
# Use an environment variable for the API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def solve_captcha_with_llm(captcha_src):
    
    try:
        # Use a different model, e.g., gemini-pro-vision
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate content
        response = model.generate_content([captcha_src, "What is the text in this CAPTCHA image?"])
        
        # Extract the CAPTCHA solution from the response
        captcha_solution = response.text.strip()
        
        return captcha_solution
    except Exception as e:
        raise Exception(f"Error in CAPTCHA solving: {str(e)}")

def analyze_content(content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "You are a helpful assistant that analyzes scientific content.",
            f"Analyze the following scientific content and provide a brief summary:\n\n{content}"
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Error in content analysis: {str(e)}")
        return "Error occurred during content analysis"
