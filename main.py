import os
import time
import pandas as pd
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import BASE_CATEGORIES, MAX_PAGES, MAX_PRODUCTS, SOURCE_SITE, CURRENCY, REGION
from scraper import scroll_and_load_products, get_product_cards, go_to_next_page, scrape_product_details


def main():
    # === SETUP ===
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    os.makedirs("output", exist_ok=True)

    try:
        for category_name, category_url in BASE_CATEGORIES.items():
            print(f"\n==============================")
            print(f"  Scraping Category: {category_name}")
            print(f"==============================")

            driver.get(category_url)
            time.sleep(5)

            scraped_data = []
            current_page = 1
            total_products_scraped = 0

            while current_page <= MAX_PAGES and total_products_scraped < MAX_PRODUCTS:
                print(f"\n=== SCRAPING PAGE {current_page} ===")

                product_cards = scroll_and_load_products(driver, current_page)

                if not product_cards:
                    print(f"[WARNING] No products found on page {current_page}")
                    break

                print(f"[INFO] Found {len(product_cards)} products on page {current_page}")

                products_on_page = 0
                for i, card in enumerate(product_cards):
                    if total_products_scraped >= MAX_PRODUCTS:
                        break

                    print(f"[INFO] Processing product {total_products_scraped + 1}/{MAX_PRODUCTS} (Page {current_page}, Item {i+1})")

                    product_data = scrape_product_details(driver, card, total_products_scraped + 1)

                    if product_data:
                        product_data["category"] = category_name
                        scraped_data.append(product_data)
                        total_products_scraped += 1
                        products_on_page += 1

                    time.sleep(1.5)

                print(f"[INFO] Scraped {products_on_page} products from page {current_page}")

                if total_products_scraped < MAX_PRODUCTS and current_page < MAX_PAGES:
                    if go_to_next_page(driver, current_page):
                        current_page += 1
                    else:
                        print(f"[INFO] No more pages. Stopping at page {current_page}")
                        break
                else:
                    break

            if scraped_data:
                csv_filename = f"output/myntra_{category_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df = pd.DataFrame(scraped_data)
                df.to_csv(csv_filename, index=False, encoding='utf-8')
                print(f"\n[SUCCESS] Data saved to {csv_filename}")
                print(f"[SUCCESS] Total products scraped: {len(scraped_data)}")

                print("\n=== SCRAPING SUMMARY ===")
                print(f"Titles: {sum(1 for item in scraped_data if item['title'] != 'Unknown Title')}")
                print(f"Images: {sum(1 for item in scraped_data if item['main_image_url'] != 'No image available')}")
                print(f"Prices: {sum(1 for item in scraped_data if item['price'] > 0)}")
                print(f"Ratings: {sum(1 for item in scraped_data if item['rating'] > 0)}")
                print(f"Descriptions: {sum(1 for item in scraped_data if item['description'] != 'No description available')}")
            else:
                print(f"[WARNING] No data scraped for {category_name}")

    except Exception as e:
        print(f"[ERROR] Main scraping error: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
