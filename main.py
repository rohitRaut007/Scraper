import os
import time
import pandas as pd
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import BASE_URL, MAX_PAGES, MAX_PRODUCTS, SOURCE_SITE, CURRENCY, REGION
# from scraper import scroll_and_load_products, get_product_cards, go_to_next_page, scrape_product_details
from scraper import scroll_and_load_products, get_product_cards, go_to_next_page,scrape_product_details


def main():
    # === SETUP ===
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    scraped_data = []
    current_page = 1
    total_products_scraped = 0

    try:
        driver.get(BASE_URL)
        time.sleep(5)

        while current_page <= MAX_PAGES and total_products_scraped < MAX_PRODUCTS:
            print(f"\n=== SCRAPING PAGE {current_page} ===")

            # Load products on current page
            product_cards = scroll_and_load_products(driver, current_page)

            if not product_cards:
                print(f"[WARNING] No products found on page {current_page}")
                break

            print(f"[INFO] Found {len(product_cards)} products on page {current_page}")

            # Process products on current page
            products_on_page = 0
            for i, card in enumerate(product_cards):
                if total_products_scraped >= MAX_PRODUCTS:
                    break

                print(f"[INFO] Processing product {total_products_scraped + 1}/{MAX_PRODUCTS} (Page {current_page}, Item {i+1})")

                product_data = scrape_product_details(driver, card, total_products_scraped + 1)

                if product_data:
                    scraped_data.append(product_data)
                    total_products_scraped += 1
                    products_on_page += 1

                time.sleep(2)  # Brief pause between products

            print(f"[INFO] Successfully scraped {products_on_page} products from page {current_page}")

            # Try to go to next page
            if total_products_scraped < MAX_PRODUCTS and current_page < MAX_PAGES:
                if go_to_next_page(driver, current_page):
                    current_page += 1
                else:
                    print(f"[INFO] No more pages available. Stopping at page {current_page}")
                    break
            else:
                break

        # === SAVE TO CSV ===
        if scraped_data:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            csv_filename = f"output/myntra_dresses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(scraped_data)
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"\n[SUCCESS] Data saved to {csv_filename}")
            print(f"[SUCCESS] Total products scraped: {len(scraped_data)}")
            print(f"[SUCCESS] Pages scraped: {current_page}")

            # Print summary
            print("\n=== SCRAPING SUMMARY ===")
            print(f"Products with titles: {sum(1 for item in scraped_data if item['title'] != 'Unknown Title')}")
            print(f"Products with images: {sum(1 for item in scraped_data if item['main_image_url'] != 'No image available')}")
            print(f"Products with prices: {sum(1 for item in scraped_data if item['price'] > 0)}")
            print(f"Products with ratings: {sum(1 for item in scraped_data if item['rating'] > 0)}")
            print(f"Products with descriptions: {sum(1 for item in scraped_data if item['description'] != 'No description available')}")
        else:
            print("No data scraped!")

    except Exception as e:
        print(f"[ERROR] Main scraping error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()