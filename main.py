from ContentGenerator import StoreContentGenerator
from pprint import pprint
import json
store = "tienda_ecologica"
products = "productos ecologicos y sostenibles"
content_generator = StoreContentGenerator(store, products)


content_generator.start_content_structure()
content_generator.set_section_categories()
content_generator.set_homepage()
content_generator.set_blog()
content_generator.save_content()

pprint(content_generator.get_current_content())


# with open("content.json", "r") as file:
#     content = json.load(file)
#
# print(content['tienda_ecologica']['Secciones']['Hogar y limpieza']['Categorías']['Limpieza del hogar']['Productos'])


