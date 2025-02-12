# 🔍 SCI Case Status Scraper

A powerful and automated tool for scraping and analyzing case status information from the Supreme Court of India website.

## ✨ Features

- 🤖 Automated case status retrieval using diary numbers
- 📝 Intelligent CAPTCHA solving capabilities
- 📊 Data extraction and analysis
- 💾 CSV export functionality
- 🧠 LLM integration for content analysis
- 🔄 Automatic retry mechanism for failed requests
- 📋 Comprehensive error handling

## 💻 Code Examples

### Installation Steps
```python
# 1. Clone the repository
# git clone https://github.com/mohitkr04/SCI_SCRAPER.git
# cd SCI_SCRAPER

# 2. Install requirements from requirements.txt
# pip install -r requirements.txt
```

### Main Script (main.py)
```python
from sci_scraper import SCIScraper
from llm_integration import analyze_content
import time
from selenium.common.exceptions import NoSuchWindowException

def main():
    retry_delay = 5  # seconds
    max_retries = 3  # Maximum number of retries
    
    # Configure parameters
    start_diary_no = 1
    end_diary_no = 10000  # Adjust as needed
    year = 2024
    
    scraper = SCIScraper()
    results = []
    
    try:
        for diary_no in range(start_diary_no, end_diary_no + 1):
            # Scraping logic here
            case_data = scraper.get_case_status(diary_no, year)
            if case_data:
                results.append(case_data)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
```

### Scraper Class (sci_scraper.py)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

class SCIScraper:
    def __init__(self, url="https://www.sci.gov.in/case-status-diary-no/"):
        self.driver = webdriver.Chrome()
        self.url = url
        
    def get_case_status(self, diary_no, year):
        try:
            self.driver.get(self.url)
            # Implementation of case status retrieval
            return case_data
        except Exception as e:
            print(f"Error retrieving case status: {str(e)}")
            return None
            
    def cleanup(self):
        self.driver.quit()
```

### CAPTCHA Solver (captcha_solver.py)
```python
import pytesseract
from PIL import Image

def solve_captcha(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error solving CAPTCHA: {str(e)}")
        return None
```

### LLM Integration (llm_integration.py)
```python
def analyze_content(text):
    # Implement your LLM analysis logic here
    analyzed_data = {
        'summary': 'Case summary...',
        'key_points': ['Point 1', 'Point 2'],
        'recommendations': ['Rec 1', 'Rec 2']
    }
    return analyzed_data
```

### Data Analysis (analyzer.py)
```python
def analyze_case_data(case_data):
    # Implement case data analysis
    analysis_results = {
        'status': case_data.get('status'),
        'timeline': case_data.get('timeline'),
        'metrics': calculate_metrics(case_data)
    }
    return analysis_results

def calculate_metrics(data):
    # Implement metrics calculation
    return {
        'processing_time': 'X days',
        'current_stage': 'Stage Y',
        'priority_level': 'Z'
    }
```

## 📋 Requirements
```txt
selenium
pytesseract
Pillow
requests
beautifulsoup4
```

## ⚠️ Important Notes

1. Ensure compliance with the Supreme Court of India's website terms of service
2. Use the tool responsibly with appropriate delays between requests
3. Keep your Chrome WebDriver updated to match your Chrome browser version

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
