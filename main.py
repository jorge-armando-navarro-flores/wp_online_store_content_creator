from ContentGenerator import StoreContentGenerator
from pprint import pprint
store = "tienda_ecologica"
products = "productos ecologicos y sostenibles"
content_generator = StoreContentGenerator(store, products)


content_generator.start_content_structure()
print('START', content_generator.get_current_content())
content_generator.set_section_categories()
print('END', content_generator.get_current_content())


