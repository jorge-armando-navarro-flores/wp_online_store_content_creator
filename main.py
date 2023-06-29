from ContentGenerator import StoreContentGenerator
from pprint import pprint
import json
import os
from amazon_product_scraper import AmazonProductScraper
PRODUCTS = os.environ.get("PRODUCTS")
STORE = f"Tienda en linea de {PRODUCTS}"
CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
DOWNLOAD_IMAGE_PATH = os.environ.get("IMAGE_PATH")
SITE_URL = os.environ.get("SITE_URL")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_PASSWORD = os.environ.get("WP_PASSWORD")


# content_generator = StoreContentGenerator(store, products)
# content_generator.load_checkpoint()
# content_generator.load_content()
# content_generator.start_content_structure()
# content_generator.set_categories()
# content_generator.set_subcategories()
# content_generator.set_products()
# content_generator.set_products_articles()
# content_generator.set_product_reviews()
# content_generator.set_blog()
# content_generator.set_homepage()
# content_generator.set_blog_articles()
# content_generator.save_content()
# print("\n-------CONTENT SAVED-------\n")
# print(content_generator.get_current_content())

def create_path_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created path: {path}")
    else:
        print(f"Path already exists: {path}")

# Example usage


with open("content.json", "r") as file:
    content = json.load(file)

scraper = AmazonProductScraper(CHROME_DRIVER_PATH, USERNAME, PASSWORD)
scraper.login()

for category in content['menu']['productos']['categorias']:
    for subcategory in category['subcategorias']:
        download_image_path = f"images/{category['nombre']}/{subcategory['nombre']}/"
        create_path_if_not_exists(download_image_path)
        scraper.search_products(subcategory['productos'], download_image_path)
        scraper.process_images(download_image_path)
        # for product in subcategory['productos']:
        #     print("---PRODUCT---")
        #     print(product)

with open("content.json", "w") as file:
    json.dump(content, file)






