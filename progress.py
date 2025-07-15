# progress.py
import os
import json
import logging

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PROGRESS_FILE = "progress_tracker.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        logging.info(f"Progress file {PROGRESS_FILE} not found. Starting fresh.")
        return {}
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logging.error(f"Invalid progress file format: Expected dictionary, got {type(data)}. Resetting to empty.")
                return {}
            return data
    except json.JSONDecodeError:
        logging.error(f"Failed to decode {PROGRESS_FILE}. Resetting to empty.")
        return {}
    except Exception as e:
        logging.error(f"Error reading {PROGRESS_FILE}: {e}. Resetting to empty.")
        return {}

def save_progress(data):
    if not isinstance(data, dict):
        logging.error(f"Attempted to save invalid progress data: {data}. Skipping save.")
        return
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logging.info(f"Progress saved to {PROGRESS_FILE}")
    except Exception as e:
        logging.error(f"Failed to save progress to {PROGRESS_FILE}: {e}")

def get_last_scraped_page(category):
    data = load_progress()
    category_progress = data.get(category, {"page": 1, "last_product_index": 0})
    if not isinstance(category_progress, dict):
        logging.warning(f"Invalid progress data for {category}: {category_progress}. Resetting to page 1, index 0.")
        return 1, 0
    return category_progress.get("page", 1), category_progress.get("last_product_index", 0)

def update_last_scraped_page(category, page, last_product_index):
    data = load_progress()
    data[category] = {"page": page, "last_product_index": last_product_index}
    save_progress(data)