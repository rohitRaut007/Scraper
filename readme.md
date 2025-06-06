# 🛍️ Myntra Web Scraper

This project is a Python-based web scraper designed to extract product details from the women's dresses section of [Myntra](https://www.myntra.com/women-dresses). It uses **Selenium** for web scraping and **Pandas** for data storage, saving the scraped data into a timestamped CSV file.

---

## ✨ Features

- Scrapes product details including:
  - Title
  - Brand
  - Price
  - Rating
  - Images (main & other)
  - Sizes
  - Description
  - Style tags
- Supports pagination (up to configurable limit).
- Handles infinite scrolling & dynamic content.
- Generates a CSV file with a timestamped name in the `output/` directory.
- Modular design with separate files for configuration, scraping logic, and utilities.

---

## 🧰 Requirements

- Python 3.8 or higher  
- Google Chrome browser  
- Required Python packages listed in `requirements.txt`

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/myntra-web-scraper.git
cd myntra-web-scraper
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ✅ Verify Chrome Browser

Make sure Google Chrome is installed. The script uses `webdriver_manager` to automatically manage ChromeDriver.

---

## 📁 File Structure

```
Scraper/
├── config.py           # Configuration settings (URLs, limits, etc.)
├── main.py             # Entry point for running the scraper
├── scraper.py          # Core scraping logic and product detail extraction
├── utils.py            # Utility functions for safe element finding
├── requirements.txt    # List of Python dependencies
└── output/             # Output CSV files
    └── myntra_dresses_YYYYMMDD_HHMMSS.csv
```

---

## 🚀 Usage

### Run the Scraper

```bash
cd path/to/Scraper
python main.py
```

### Behavior

- Opens Chrome browser.
- Navigates to the Myntra women’s dresses section.
- Scrapes up to `MAX_PRODUCTS` (default 100) across `MAX_PAGES` (default 5).
- Saves the results as a CSV in the `output/` folder with timestamped filename.

---

## 📦 Output

CSV file with the following columns:

| Column            | Description                                |
|-------------------|--------------------------------------------|
| `id`              | Unique UUID for each product               |
| `title`           | Product title                              |
| `brand`           | Product brand                              |
| `main_image_url`  | Primary product image                      |
| `other_images_url`| List of additional image URLs              |
| `sourceSite`      | Source site (Myntra)                       |
| `source_url`      | Product page URL                           |
| `rating`          | Rating out of 5                            |
| `numOfUserRated`  | Number of ratings                          |
| `price`           | Product price                              |
| `currency`        | Currency (INR)                             |
| `region`          | Region (India)                             |
| `sizes_available` | Available sizes                            |
| `gender`          | Gender (w for women)                       |
| `category`        | Category (western_wear)                    |
| `clothing_type`   | Clothing type (dress)                      |
| `description`     | Product description                        |
| `style_tags`      | Dictionary of style attributes             |
| `created_At`      | Timestamp of data creation (GMT)           |
| `updated_At`      | Timestamp of last update (GMT)             |

---

### ⚙️ Configuration
Edit `config.py` to customize the scraper:

---

## 🛠️ Troubleshooting

### Selenium / ChromeDriver Errors

- Ensure Google Chrome is installed and up to date.
- `webdriver_manager` should handle ChromeDriver, but clear the cache if issues occur.
- Try running script with admin privileges.

### No Data Scraped

- Confirm internet connection.
- Check `BASE_URL` is correct and accessible.
- HTML structure changes may require updating selectors in `scraper.py`.

### VS Code Issues

- Avoid using Code Runner; instead, run:
  ```bash
  python main.py
  ```
- Delete temporary files like `tempCodeRunnerFile.py`.

---

## 📌 Notes

- **Date**: Documentation accurate as of **June 4, 2025**
- **Limitations**: Built specifically for the "women-dresses" section of Myntra.
- **Performance**: Sleep intervals are added to avoid overwhelming the server.
- **Legal**: Use responsibly and respect [Myntra’s terms of service](https://www.myntra.com/termsofuse).

---

## 🤝 Contributing

- Fork this repository  
- Submit PRs for improvements  
- Report issues or request features  

---

## 📝 License

This project is provided **as-is** for educational purposes. No warranty is implied. Use at your own risk.
