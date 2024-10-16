from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import io
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup
from llm_integration import analyze_content

class SCIScraper:
    def __init__(self, url="https://www.sci.gov.in/case-status-diary-no/"):
        self.driver = webdriver.Chrome()
        self.url = url
        self.captcha_timeout = 20

    def scrape_and_save(self, num_pages=5):
        self.driver.get(self.url)
        data = []

        for page in range(1, num_pages + 1):
            try:
                self.solve_and_submit_captcha()
                
                # Wait for results and scrape data
                results = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "cnrResultsDetails"))
                )

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                diary_entries = soup.find_all(class_="diary-entry")

                for entry in diary_entries:
                    details = self.extract_details(entry)
                    data.append(details)

                # Navigate to next page or break if no more pages
                if not self.go_to_next_page():
                    break

            except TimeoutException:
                print(f"Timeout on page {page}. Saving debug info and continuing...")
                self.save_debug_info()
                continue

        self.save_to_csv(data)

    def solve_and_submit_captcha(self):
        captcha_img = WebDriverWait(self.driver, self.captcha_timeout).until(
            EC.presence_of_element_located((By.ID, "captcha_image"))
        )
        captcha_src = captcha_img.get_attribute('src')
        captcha_solution = self.solve_captcha(captcha_src)
        
        captcha_input = self.driver.find_element(By.ID, "captcha")
        captcha_input.send_keys(captcha_solution)
        
        submit_button = self.driver.find_element(By.ID, "getDetails")
        submit_button.click()

    def solve_captcha(self, captcha_src):
        import base64
        img_data = base64.b64decode(captcha_src.split(',')[1])
        img = Image.open(io.BytesIO(img_data))
        img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        captcha_text = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789')
        return ''.join(filter(str.isdigit, captcha_text))

    def extract_details(self, entry):
        diary_no = entry.find(class_="diary_no").text.strip()
        year = entry.find(class_="year").text.strip()
        title_element = entry.find('h2')
        title = title_element.text.strip() if title_element else "N/A"
        link_element = entry.find('a')
        link = link_element['href'] if link_element else "N/A"
        
        # Analyze content using LLM (you'll need to implement this function)
        analysis = analyze_content(self.get_html(link) if link != "N/A" else "")
        
        return {
            'Diary No': diary_no,
            'Year': year,
            'Title': title,
            'Link': link,
            'Analysis': analysis
        }

    def go_to_next_page(self):
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, '.next-button')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(2)  # Wait for page to load
                return True
            return False
        except NoSuchElementException:
            return False

    def get_html(self, url=None):
        if url:
            self.driver.get(url)
        return self.driver.page_source

    def save_to_csv(self, data, filename='output.csv'):
        if not data:
            print("No data to save.")
            return
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Data saved to {filename}")

    def save_debug_info(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"debug_info_{timestamp}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"Debug info saved to {filename}")

    def close(self):
        self.driver.quit()

    def scrape_data(self, start_diary_no, end_diary_no, start_year, end_year):
        data = []
        for year in range(start_year, end_year + 1):
            for diary_no in range(start_diary_no, end_diary_no + 1):
                try:
                    self.driver.get(self.url)
                    self.solve_and_submit_captcha()
                    
                    # Fill in the diary number and year
                    diary_input = self.driver.find_element(By.ID, "diary_no")
                    diary_input.send_keys(str(diary_no))
                    
                    year_input = self.driver.find_element(By.ID, "diary_year")
                    year_input.send_keys(str(year))
                    
                    submit_button = self.driver.find_element(By.ID, "getDetails")
                    submit_button.click()
                    
                    # Wait for results and scrape data
                    results = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "cnrResultsDetails"))
                    )
                    
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    entry = soup.find(class_="diary-entry")
                    
                    if entry:
                        details = self.extract_details(entry)
                        data.append(details)
                    
                except TimeoutException:
                    print(f"Timeout for Diary No {diary_no}, Year {year}. Saving debug info and continuing...")
                    self.save_debug_info()
                    continue
        
        return data

# Usage
if __name__ == "__main__":
    scraper = SCIScraper()
    try:
        scraper.scrape_and_save(num_pages=5)
    finally:
        scraper.close()
