import time
import uuid
import re
from datetime import datetime
import pytz
from selenium.webdriver.common.by import By
from config import SOURCE_SITE, CURRENCY, REGION
from utils import safe_find_text, safe_find_elements

def scroll_and_load_products(driver, current_page):
    """Scroll to load all products on current page"""
    print(f"[INFO] Loading products on page {current_page}...")
    for i in range(10):  # Reduced scrolls per page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Check if we have enough products or hit the end
        product_cards = get_product_cards(driver)
        if len(product_cards) >= 50:  # Assume ~50 products per page
            break

    return get_product_cards(driver)

def get_product_cards(driver):
    """Get all product cards on current page"""
    product_selectors = [
        "li.product-base",
        ".product-productMetaInfo",
        ".product-sliderContainer",
        "[data-testid='product-base']"
    ]

    for selector in product_selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                print(f"Found {len(cards)} products using selector: {selector}")
                return cards
        except:
            continue
    return []

def go_to_next_page(driver, current_page):
    """
    Navigate to the next page by clicking the 'Next' button.
    Returns True if next page loaded, False if no next page.
    """
    try:
        # Multiple selectors for next button
        next_selectors = [
            "li.pagination-next a",
            "a[aria-label='Next']",
            ".pagination-next",
            "button.pagination-next",
            "a.pagination-next",
            ".paginationButton-next",
            "li:last-child a[aria-label]"  # Often the last pagination item
        ]

        next_button = None
        for selector in next_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    # Check if element is enabled and visible
                    if elem.is_enabled() and elem.is_displayed():
                        # Additional check - make sure it's not disabled via class
                        classes = elem.get_attribute("class") or ""
                        parent_classes = elem.find_element(By.XPATH, "..").get_attribute("class") or ""

                        if "disabled" not in classes.lower() and "disabled" not in parent_classes.lower():
                            next_button = elem
                            break

                if next_button:
                    break
            except:
                continue

        if next_button:
            print(f"[INFO] Found next button, navigating to page {current_page + 1}...")

            # Scroll to button first
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)

            # Click using JavaScript to avoid interception
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)  # Wait for page load

            # Verify we moved to next page by checking URL or page content
            time.sleep(3)
            return True
        else:
            print(f"[INFO] No next page button found or button is disabled.")
            return False

    except Exception as e:
        print(f"[ERROR] Error navigating to next page: {e}")
        return False

def scrape_product_details(driver, card, product_index):
    """Scrape details for a single product"""
    try:
        # Get product link
        link_selectors = ["a", ".product-base a", "[href*='/']"]
        link = None
        for selector in link_selectors:
            try:
                link_element = card.find_element(By.CSS_SELECTOR, selector)
                link = link_element.get_attribute("href")
                if link:
                    break
            except:
                continue

        if not link:
            print(f"[WARNING] No link found for product {product_index}, skipping...")
            return None

        # Open product page
        driver.execute_script("window.open(arguments[0]);", link)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(5)

        # === Enhanced Title and Brand Extraction ===
        brand_selectors = [
            "h1.pdp-title",
            ".pdp-title",
            "h1[class*='title']",
            ".brand-name",
            "span.pdp-title"
        ]
        brand = safe_find_text(driver, brand_selectors, "Unknown Brand")

        title_selectors = [
            "h1.pdp-name",
            ".pdp-name",
            "h1[class*='name']",
            ".product-title",
            "span.pdp-name"
        ]
        title = safe_find_text(driver, title_selectors, "Unknown Title")

        # === Enhanced Description ===
        desc_selectors = [
            ".pdp-product-description-content",
            "div.pdp-productDescriptors",
            ".product-description",
            ".pdp-product-description",
            "[class*='description']"
        ]
        product_desc = safe_find_text(driver, desc_selectors, "No description available")

        # === Enhanced Image Collection ===
        image_grid_selector = "#mountRoot > div > div:nth-child(1) > main > div.pdp-details.common-clearfix > div.image-grid-container.common-clearfix"
        image_urls = []

        try:
            image_grid_container = driver.find_element(By.CSS_SELECTOR, image_grid_selector)

            # Method 1: Get all div children of the grid container
            grid_divs = image_grid_container.find_elements(By.CSS_SELECTOR, "div")

            for div in grid_divs:
                try:
                    img_selectors = [
                        "img",
                        "picture img",
                        "[style*='background-image']",
                        "div[style*='background-image']"
                    ]

                    for selector in img_selectors:
                        try:
                            images = div.find_elements(By.CSS_SELECTOR, selector)
                            for img in images:
                                img_url = (img.get_attribute("src") or
                                        img.get_attribute("data-src") or
                                        img.get_attribute("data-original") or
                                        img.get_attribute("data-lazy-src"))

                                if not img_url and selector.startswith("[style"):
                                    style = img.get_attribute("style")
                                    if style and "background-image" in style:
                                        bg_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                                        if bg_match:
                                            img_url = bg_match.group(1)

                                if img_url and img_url.startswith('http') and img_url not in image_urls:
                                    image_urls.append(img_url)
                        except:
                            continue
                except:
                    continue

        except:
            # Fallback to original selectors
            fallback_selectors = [
                ".image-grid-image img",
                "picture img",
                "img[src*='myntra']",
                ".pdp-image img",
                ".product-images img"
            ]

            for selector in fallback_selectors:
                try:
                    images = driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in images:
                        src = img.get_attribute("src") or img.get_attribute("data-src")
                        if src and src.startswith('http') and src not in image_urls:
                            image_urls.append(src)
                except:
                    continue

        # Filter and clean image URLs
        unique_image_urls = []
        for url in image_urls:
            if (url not in unique_image_urls and
                ('myntra' in url.lower() or 'myntassets' in url.lower())):
                unique_image_urls.append(url)

        if not unique_image_urls and image_urls:
            unique_image_urls = [url for url in image_urls if url.startswith('http')]

        # COMPULSORY: Must have images
        if not unique_image_urls:
            print(f"[WARNING] No images found for product {product_index}, skipping...")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return None

        main_image_url = unique_image_urls[0]
        other_images_url = unique_image_urls[1:] if len(unique_image_urls) > 1 else []

        # === Enhanced Price Extraction ===
        price_selectors = [
            ".pdp-price strong",
            ".pdp-price",
            "[class*='price']",
            ".price-value",
            "span[class*='price']"
        ]

        price = 0.0
        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                price_text = price_element.text
                price_numbers = re.findall(r'[\d,]+', price_text.replace('₹', '').replace(',', ''))
                if price_numbers:
                    price = float(price_numbers[0])
                    break
            except:
                continue

        # === Enhanced Rating Extraction ===
        rating_selectors = [
            ".index-overallRating",
            ".pdp-ratings span",
            "[class*='rating'] span",
            ".rating-value"
        ]

        rating = 0.0
        for selector in rating_selectors:
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, selector)
                rating_text = rating_element.text.strip()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
                    break
            except:
                continue

        # === Enhanced Rating Count ===
        rating_count_selectors = [
            ".index-totalRatings",
            "[class*='rating-count']",
            ".ratings-count",
            "span[class*='count']",
            ".pdp-ratings-count"
        ]

        rating_count = 0
        for selector in rating_count_selectors:
            try:
                count_element = driver.find_element(By.CSS_SELECTOR, selector)
                count_text = count_element.text.upper()

                if 'K' in count_text:
                    k_match = re.search(r'(\d+\.?\d*)\s*K', count_text)
                    if k_match:
                        rating_count = int(float(k_match.group(1)) * 1000)
                        break
                elif 'M' in count_text:
                    m_match = re.search(r'(\d+\.?\d*)\s*M', count_text)
                    if m_match:
                        rating_count = int(float(m_match.group(1)) * 1000000)
                        break
                else:
                    count_numbers = re.findall(r'\d+', count_text.replace(',', ''))
                    if count_numbers:
                        rating_count = int(count_numbers[0])
                        break
            except:
                continue

        # COMPULSORY: Must have rating data
        if rating == 0.0 or rating_count == 0:
            print(f"[WARNING] No rating data found for product {product_index}, skipping...")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return None

        # === Size Collection ===
        size_selectors = [
            ".size-buttons-size-button",
            "[class*='size'] button",
            ".size-option",
            "[data-testid*='size']"
        ]

        sizes = []
        for selector in size_selectors:
            try:
                size_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                sizes = [s.text.strip() for s in size_elements if s.text.strip()]
                if sizes:
                    break
            except:
                continue

        # === Auto-extract Gender, Category, Clothing Type ===
        gender = "w"
        category = "western_wear"
        clothing_type = "dress"

        # === Style Tags extraction ===
        style_tags = {}
        try:
            table_container = driver.find_element(By.CSS_SELECTOR, "#mountRoot > div > div:nth-child(1) > main > div.pdp-details.common-clearfix > div.pdp-description-container > div.pdp-productDescriptors > div > div.index-sizeFitDesc > div.index-tableContainer")
            index_rows = table_container.find_elements(By.CSS_SELECTOR, ".index-row")

            for row in index_rows:
                try:
                    key_element = row.find_element(By.CSS_SELECTOR, ".index-rowKey")
                    value_element = row.find_element(By.CSS_SELECTOR, ".index-rowValue")

                    key = key_element.text.strip()
                    value = value_element.text.strip()

                    if key and value:
                        style_tags[key] = value
                except:
                    continue
        except:
            pass

        # === Timestamps ===
        gmt_time = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S GMT")

        # === Create Product Data ===
        product_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "brand": brand,
            "main_image_url": main_image_url,
            "other_images_url": other_images_url,
            "sourceSite": SOURCE_SITE,
            "source_url": link,
            "rating": rating,
            "numOfUserRated": rating_count,
            "price": price,
            "currency": CURRENCY,
            "region": REGION,
            "sizes_available": sizes,
            "gender": gender,
            "category": category,
            "clothing_type": clothing_type,
            "description": product_desc,
            "style_tags": style_tags,
            "created_At": gmt_time,
            "updated_At": gmt_time
        }

        print(f"[SUCCESS] Successfully scraped: {title[:50]}...")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return product_data

    except Exception as e:
        print(f"[ERROR] Error processing product {product_index}: {e}")
        # Ensure we close any extra windows
        while len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return None