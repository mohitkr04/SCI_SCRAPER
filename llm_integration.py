import google.generativeai as genai

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyCpM8r5L_r8NXfFgAqZ0N3q1k6tawER8lw")

def analyze_content(content):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([
            "You are a helpful assistant that analyzes scientific content.",
            f"Analyze the following scientific content and provide a brief summary:\n\n{content}"
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Error in content analysis: {str(e)}")
        return "Error occurred during content analysis"

