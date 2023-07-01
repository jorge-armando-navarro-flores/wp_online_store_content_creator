from ContentGenerator import StoreContentGenerator
from pprint import pprint
import json
import os
from amazon_product_scraper import AmazonProductScraper
from wp_content_uploader import ContentUploader
PRODUCTS = os.environ.get("PRODUCTS")
STORE = f"Tienda en linea de {PRODUCTS}"

DOWNLOAD_IMAGE_PATH = os.environ.get("IMAGE_PATH")
SITE_URL = os.environ.get("SITE_URL")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_PASSWORD = os.environ.get("WP_PASSWORD")


content_generator = StoreContentGenerator(STORE, PRODUCTS)
content_generator.load_checkpoint()
content_generator.load_content()
content_generator.start_content_structure()
content_generator.set_homepage()
content_generator.set_categories()
content_generator.set_subcategories()
content_generator.set_products()
content_generator.set_product_reviews()
content_generator.set_products_articles()
content_generator.set_blog()
content_generator.set_blog_articles()

content_generator.save_content()
print("\n-------CONTENT SAVED-------\n")
print(content_generator.get_current_content())










