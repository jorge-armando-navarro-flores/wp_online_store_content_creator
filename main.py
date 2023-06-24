from ContentGenerator import StoreContentGenerator
from pprint import pprint
import json

products = "Productos Ecologicos y Sostenibles"
store = f"Tienda en linea de {products}"

content_generator = StoreContentGenerator(store, products)

content_generator.start_content_structure()
print("\n--------INITIAL STRUCTURE SET-------\n")
content_generator.set_categories()
print("\n-------CATEGORIES SET-------\n")
content_generator.set_subcategories()
print("\n-------SUBCATEGORIES SET-------\n")
content_generator.set_products()
print("\n-------PRODUCTS SET-------\n")
content_generator.save_content()
print("\n-------CONTENT SAVED-------\n")

print(content_generator.get_current_content())


# with open("content.json", "r") as file:
#     content = json.load(file)
#
# print(content['tienda_ecologica'])


