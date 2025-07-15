from selenium.webdriver.common.by import By
import time

def safe_find_text(driver, selectors, fallback="Unknown"):
    """Try multiple selectors and return first match or fallback"""
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            if text:
                return text
        except:
            continue
    return fallback

def safe_find_elements(driver, selectors):
    """Try multiple selectors for elements"""
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return elements
        except:
            continue
    return []


def get_total_pages(driver):
    try:
        # Wait a moment for pagination to load
        time.sleep(2)

        pagination_text_element = driver.find_element(By.CSS_SELECTOR, "li.pagination-paginationMeta")
        if pagination_text_element:
            text = pagination_text_element.text.strip()
            # Example format: "Page 1 of 32"
            if "of" in text:
                return int(text.split("of")[1].strip())
    except Exception as e:
        print(f"[WARNING] Could not determine total pages dynamically: {e}")
    
    # fallback
    return 5
