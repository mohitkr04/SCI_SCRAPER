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
from llm_integration import analyze_content, solve_captcha_with_llm
import requests
import PyPDF2

class SCIScraper:
    def __init__(self, url="https://www.sci.gov.in/case-status-diary-no/"):
        self.driver = webdriver.Chrome()
        self.url = url
        self.api_url = "https://www.sci.gov.in/wp-admin/admin-ajax.php"
        self.session = requests.Session()
        self.captcha_timeout = 20

    def scrape_and_save(self, start_diary_no, end_diary_no, year, output_file):
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Diary No', 'Year', 'Case No', 'Petitioner', 'Respondent', 'Pet. Advocate', 'Resp. Advocate', 'Last Listed On', 'Status', 'Last Order']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            data_found = False
            for diary_no in range(start_diary_no, end_diary_no + 1):
                print(f"Processing Diary No: {diary_no}")
                captcha_solution = self.solve_and_submit_captcha()
                json_data = self.fetch_data(diary_no, year, captcha_solution)
                
                if 'bt-content' in json_data:
                    content = json_data['bt-content']
                    case_details = self.extract_case_details(content)
                    
                    if case_details:
                        data_found = True
                        row = {
                            'Diary No': diary_no,
                            'Year': year,
                            'Case No': case_details.get('Case No', ''),
                            'Petitioner': case_details.get('Petitioner', ''),
                            'Respondent': case_details.get('Respondent', ''),
                            'Pet. Advocate': case_details.get('Pet. Advocate', ''),
                            'Resp. Advocate': case_details.get('Resp. Advocate', ''),
                            'Last Listed On': case_details.get('Last Listed On', ''),
                            'Status': case_details.get('Status', ''),
                            'Last Order': case_details.get('Last Order', '')
                        }
                        writer.writerow(row)
                    else:
                        print(f"No details found for Diary No: {diary_no}")
                else:
                    print(f"No data found for Diary No: {diary_no}")

        if data_found:
            print(f"Data saved to {output_file}")
        else:
            print("No data found for any of the specified diary numbers.")

    def solve_and_submit_captcha(self):
        response = self.session.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        captcha_img = soup.find('img', id='siwp_captcha_image_0')
        
        # Ensure the CAPTCHA image is found
        if captcha_img:
            # Get the CAPTCHA image source and replace "&amp;" with "&"
            captcha_src = captcha_img['src'].replace("&amp;", "&")
        else:
            print("CAPTCHA image not found.")
            return ""  # Handle the case where the CAPTCHA image is not found

        try:
            # Attempt to solve captcha using LLM
            captcha_solution = solve_captcha_with_llm(captcha_src)
            # Fill the CAPTCHA input field with the solution
            captcha_input = self.driver.find_element(By.ID, "siwp_captcha_value_0")
            captcha_input.send_keys(captcha_solution)  # Fill the input field with the CAPTCHA solution
        except Exception as e:
            print(f"Error in CAPTCHA solving: {str(e)}")
            print("Falling back to manual CAPTCHA input.")
            
            # Find the CAPTCHA input field and use the class
            captcha_input = soup.find('input', class_='siwp-captcha-cntr')
            if captcha_input:
                captcha_solution = input("Please enter the CAPTCHA solution manually: ")
                captcha_input.send_keys(captcha_solution)  # Fill the input field with the manually entered solution
            else:
                print("CAPTCHA input field not found. Please check the page structure.")
                captcha_solution = ""  # Set to empty or handle as needed
        
        return captcha_solution

    def fetch_data(self, diary_no, year, captcha_solution):
        params = {
            'diary_no': diary_no,
            'year': year,
            'scid': '6wsamyv0cs7ifrwamoif0lvl0meds5lc71monzzh',  # This might need to be dynamically obtained
            'tok_8e7180d3a2bc6bbc3147e43b0b4b82b1daebd789': '5936f5af4a9f6b1dc65bc57b528ec9b491f64077',  # This might need to be dynamically obtained
            'siwp_captcha_value': captcha_solution,
            'es_ajax_request': '1',
            'submit': 'Search',
            'action': 'get_daily_order_diary_no',
            'language': 'en'
        }
        
        response = self.session.get(self.api_url, params=params)
        return response.json()

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

    def extract_pdf_content(self, pdf_url):
        response = self.session.get(pdf_url)
        pdf_content = io.BytesIO(response.content)
        
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        
        return text_content

    def extract_case_details(self, content):
        # Implement this function to extract case details from the content
        pass

# Usage
if __name__ == "__main__":
    scraper = SCIScraper()
    try:
        # Replace this line
        scraper.scrape_and_save(start_diary_no=1, end_diary_no=5, year=2023, output_file='output.csv')
    finally:
        scraper.close()
