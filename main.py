from ContentGenerator import StoreContentGenerator
from pprint import pprint
import json
import os

products = os.environ.get("PRODUCTS")
store = f"Tienda en linea de {products}"


content_generator = StoreContentGenerator(store, products)

content_generator.load_checkpoint()
content_generator.load_content()
content_generator.start_content_structure()
content_generator.set_categories()
content_generator.set_subcategories()
# content_generator.set_products()
content_generator.set_blog()
# content_generator.set_products_articles()
# content_generator.set_homepage()
content_generator.set_blog_articles()
content_generator.save_content()
print("\n-------CONTENT SAVED-------\n")
print(content_generator.get_current_content())


# with open("content.json", "r") as file:
#     content = json.load(file)
#
# print(content['tienda_ecologica'])


