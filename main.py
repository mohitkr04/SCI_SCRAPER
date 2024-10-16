from sci_scraper import SCIScraper
from llm_integration import analyze_content
import time
from selenium.common.exceptions import NoSuchWindowException

def main():
    retry_delay = 5  # seconds
    max_retries = 3  # Maximum number of retries for each diary number

    # Define the required parameters
    start_diary_no = 1
    end_diary_no = 10000  # Adjust this as needed
    year = 2024  # You can modify this or add a year range if needed

    scraper = SCIScraper()
    results = []

    try:
        for diary_no in range(start_diary_no, end_diary_no + 1):
            retries = 0
            while retries < max_retries:
                try:
                    print(f"Processing Diary No {diary_no}, Year {year}")
                    scraped_data = scraper.scrape_data(diary_no, diary_no, year, year)
                    
                    if scraped_data:
                        # Analyze the scraped content using LLM
                        for item in scraped_data:
                            analysis = analyze_content(item['Result'])
                            item['Analysis'] = analysis
                        results.extend(scraped_data)
                        print(f"Successfully processed Diary No {diary_no}")
                    else:
                        print(f"No data found for Diary No {diary_no}")
                    
                    break  # Exit the retry loop if successful
                except NoSuchWindowException:
                    print(f"Browser window closed unexpectedly. Retrying... (Attempt {retries + 1}/{max_retries})")
                    scraper.close()
                    scraper = SCIScraper()  # Reinitialize the scraper
                    retries += 1
                except Exception as e:
                    print(f"Error processing Diary No {diary_no}, Year {year}: {str(e)}")
                    try:
                        scraper.save_debug_info()
                    except NoSuchWindowException:
                        print("Could not save debug info due to closed window.")
                    break  # Exit the retry loop for other exceptions
            
            # Add a small delay between requests to avoid overwhelming the server
            time.sleep(retry_delay)

        # Save all collected results to CSV
        if results:
            scraper.save_to_csv(results, 'analyzed_scraped_data.csv')
            print("Scraping and analysis completed. Results saved to CSV.")

    finally:
        scraper.close()

if __name__ == "__main__":
    main()
