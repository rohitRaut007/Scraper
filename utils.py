from selenium.webdriver.common.by import By

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