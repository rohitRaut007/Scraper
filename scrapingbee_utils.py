# scrapingbee_utils.py

import requests
import random
import time
from config import SCRAPINGBEE_API_KEY

SCRAPINGBEE_URL = "https://app.scrapingbee.com/api/v1/"

def fetch_with_scrapingbee(url, js_render=True):
    params = {
        "api_key": SCRAPINGBEE_API_KEY,
        "url": url,
        "render_js": "true" if js_render else "false",
        "block_ads": "true",
    }

    try:
        print(f"[SCRAPINGBEE] Fetching: {url}")
        response = requests.get(SCRAPINGBEE_URL, params=params, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            print(f"[SCRAPINGBEE] Failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"[SCRAPINGBEE] Error: {e}")
        return None
