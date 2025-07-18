import os
import time
import uuid
import pandas as pd
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from utils import get_total_pages
from config import BASE_CATEGORIES, MAX_PAGES, MAX_PRODUCTS, SOURCE_SITE, CURRENCY, REGION, SCRAPERAPI_KEY
from scraper import scroll_and_load_products, get_product_cards, go_to_next_page, scrape_product_details
from db import save_product
from progress import get_last_scraped_page, update_last_scraped_page  # ✅ NEW

def create_driver():
    PROXY = f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'--proxy-server={PROXY}')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def main():
    driver = create_driver()
    os.makedirs("output", exist_ok=True)

    try:
        for category_name, category_url in BASE_CATEGORIES.items():
            print(f"\n==============================")
            print(f"  Scraping Category: {category_name}")
            print(f"==============================")

            driver.get(category_url)
            time.sleep(5)

            scraped_data = []
            current_page = get_last_scraped_page(category_name)  # ✅ Resume from last page
            total_products_scraped = 0
            max_pages = get_total_pages(driver) or MAX_PAGES

            while current_page <= max_pages and total_products_scraped < MAX_PRODUCTS:
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

                    print(f"[INFO] Processing product {total_products_scraped + 1}/{MAX_PRODUCTS} (Page {current_page}, Item {i + 1})")

                    raw_data = scrape_product_details(driver, card, total_products_scraped + 1)
                    if raw_data:
                        product_data = {
                            "id": str(uuid.uuid4()),
                            "title": raw_data.get("title", "").strip(),
                            "brand": raw_data.get("brand", "").strip(),
                            "main_image_url": raw_data.get("main_image_url", ""),
                            "other_images_url": raw_data.get("other_images_url", []),
                            "sourceSite": SOURCE_SITE,
                            "source_url": raw_data.get("source_url", "https://www.myntra.com/"),
                            "rating": raw_data.get("rating", 0.0),
                            "numOfUserRated": raw_data.get("numOfUserRated", 0),
                            "price": raw_data.get("price", 0),
                            "currency": CURRENCY,
                            "region": REGION,
                            "sizes_available": raw_data.get("sizes_available", ""),
                            "gender": raw_data.get("gender", "Women"),
                            "category": category_name,
                            "clothing_type": raw_data.get("clothing_type", category_name),
                            "description": raw_data.get("description", ""),
                            "style_tags": raw_data.get("style_tags", []),
                            "created_At": datetime.now(pytz.timezone("Asia/Kolkata")),
                            "updated_At": datetime.now(pytz.timezone("Asia/Kolkata"))
                        }

                        inserted = save_product(product_data)
                        if inserted:
                            scraped_data.append(product_data)
                            total_products_scraped += 1
                            products_on_page += 1
                        else:
                            print(f"[DB] Skipped product due to missing fields or DB error")

                    time.sleep(1.5)

                print(f"[INFO] Scraped {products_on_page} products from page {current_page}")
                update_last_scraped_page(category_name, current_page + 1)  # ✅ Save progress

                if total_products_scraped < MAX_PRODUCTS and current_page < MAX_PAGES:
                    if go_to_next_page(driver, current_page):
                        current_page += 1
                    else:
                        print(f"[INFO] No more pages. Stopping at page {current_page}")
                        break
                else:
                    break

            if scraped_data:
                print(f"[SUCCESS] Total products scraped and saved: {len(scraped_data)}")

                print("\n=== SCRAPING SUMMARY ===")
                print(f"Titles:       {sum(1 for item in scraped_data if item['title'])}")
                print(f"Images:       {sum(1 for item in scraped_data if item['main_image_url'])}")
                print(f"Prices:       {sum(1 for item in scraped_data if item['price'] > 0)}")
                print(f"Ratings:      {sum(1 for item in scraped_data if item['rating'] > 0)}")
                print(f"Descriptions: {sum(1 for item in scraped_data if item['description'])}")
                print(f"Pages covered: {current_page}")

            else:
                print(f"[WARNING] No data scraped or saved for {category_name}")

    except Exception as e:
        print(f"[ERROR] Main scraping error: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
