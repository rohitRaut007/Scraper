import psycopg2
from psycopg2.extras import Json
from datetime import datetime

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "myntra_scraper"
DB_USER = "postgres"
DB_PASSWORD = "pass321"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def validate_product_data(product_data):
    required_fields = [
        "id", "title", "brand", "main_image_url", "other_images_url",
        "sourceSite", "source_url", "rating", "numOfUserRated",
        "price", "currency", "region", "sizes_available", "gender",
        "category", "clothing_type", "description", "style_tags",
        "created_At", "updated_At"
    ]
    for field in required_fields:
        value = product_data.get(field)
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            print(f"[DB] Skipping insert: Field '{field}' is empty or missing")
            return False
    return True

def save_product(product_data, retry=False):
    if not validate_product_data(product_data):
        return False

    status = 'success' if not retry else 'retried'

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                insert_query = """
                INSERT INTO products (
                    id, title, brand, main_image_url, other_images_url,
                    source_site, source_url, rating, num_of_user_rated,
                    price, currency, region, sizes_available, gender,
                    category, clothing_type, description, style_tags,
                    
                    created_at, updated_at, status
                ) VALUES (
                    %(id)s, %(title)s, %(brand)s, %(main_image_url)s, %(other_images_url)s,
                    %(sourceSite)s, %(source_url)s, %(rating)s, %(numOfUserRated)s,
                    %(price)s, %(currency)s, %(region)s, %(sizes_available)s, %(gender)s,
                    %(clothing_type)s, %(category)s, %(description)s, %(style_tags)s,
                    
                    %(created_At)s, %(updated_At)s, %(status)s
                )
                ON CONFLICT (title, source_url) DO UPDATE SET
                    brand = EXCLUDED.brand,
                    main_image_url = EXCLUDED.main_image_url,
                    other_images_url = EXCLUDED.other_images_url,
                    source_site = EXCLUDED.source_site,
                    rating = EXCLUDED.rating,
                    num_of_user_rated = EXCLUDED.num_of_user_rated,
                    price = EXCLUDED.price,
                    currency = EXCLUDED.currency,
                    region = EXCLUDED.region,
                    sizes_available = EXCLUDED.sizes_available,
                    gender = EXCLUDED.gender,
                    category = EXCLUDED.category,
                    clothing_type = EXCLUDED.clothing_type,
                    description = EXCLUDED.description,
                    style_tags = EXCLUDED.style_tags,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    status = EXCLUDED.status;
                """

                cur.execute(insert_query, {
                    "id": product_data["id"],
                    "title": product_data["title"],
                    "brand": product_data["brand"],
                    "main_image_url": product_data["main_image_url"],
                    "other_images_url": Json(product_data["other_images_url"]),
                    "sourceSite": product_data["sourceSite"],
                    "source_url": product_data["source_url"],
                    "rating": product_data["rating"],
                    "numOfUserRated": product_data["numOfUserRated"],
                    "price": product_data["price"],
                    "currency": product_data["currency"],
                    "region": product_data["region"],
                    "sizes_available": product_data["sizes_available"],
                    "gender": product_data["gender"],
                    "category": product_data["category"],
                    "clothing_type": product_data["clothing_type"],
                    "description": product_data["description"],
                    "style_tags": Json(product_data["style_tags"]),
                    # "review_images": Json(product_data.get("review_images", [])),
                    # "review_texts": Json(product_data.get("review_texts", [])),
                    "created_At": product_data["created_At"],
                    "updated_At": product_data["updated_At"],
                    "status": status
                })

                conn.commit()
                print(f"[DB] Inserted/Updated product '{product_data['title']}' with status '{status}' successfully.")
                return True

    except Exception as e:
        print(f"[DB ERROR] Insert/Update failed for product '{product_data.get('title', '')}': {e}")
        if not retry:
            print("[DB] Retrying product insertion...")
            return save_product(product_data, retry=True)
        return False
