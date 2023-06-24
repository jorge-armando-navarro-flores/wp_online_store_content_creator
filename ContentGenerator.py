import openai
import os
import json
import pprint

openai.api_key = os.environ.get('OPENAI_API_KEY')


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


class StoreContentGenerator:
    def __init__(self, store, products):
        self.store = store
        self.products = products
        self.content = {}
        self.checkpoint = {
                            "start_content_structure": 0,
                            "set_categories": 0,
                            "set_subcategories": {
                                "section_idx": 0,
                                "category_idx": 0,
                                "idx": 0
                            },
                            "set_products": {
                                "category_idx": 0,
                                "subcategory_idx": 0,
                                "idx": 0
                            },
                            "set_blog": {
                                "category_idx": 0,
                                "subcategory_idx": 0,
                                "idx": 0
                            }
                        }

    def start_content_structure(self):
        print("\n--------INITIAL STRUCTURE SET-------")
        if not self.checkpoint["start_content_structure"]:
            main_menu_prompt = f"""
            Instrucciones:
            Escribe como un experto SEO.
    
            Este es un diccionario que representa un listado de las secciones que debe tener el menu principal de una {self.store}. Tu objetivo es proporcionar la estructura del diccionario en formato JSON. solo el JSON
    
            - El diccionario principal se llama "menu".
            - Cada nombre de sección debe ser una clave dentro del diccionario principal.
            - Para cada sección, incluye las siguientes claves:
                - "titulo":  nombre de la seccion.
                - "descripcion": nombre completo relacionado con {self.store}.
                - "categorizable" : 1 si es categorizable y 0 si no.
            """

            main_menu_response = get_completion(main_menu_prompt)
            main_menu_dict = json.loads(main_menu_response)

            if main_menu_dict['menu'].get('blog'):
                main_menu_dict['menu']['blog']['categorizable'] = 1

            self.content = main_menu_dict
            self.checkpoint["start_content_structure"] = 1
            self.save_checkpoint()
            self.save_content()
        print("Completed ✓\n")

    def set_categories(self):
        print("\n-------CATEGORIES SET-------")
        if not self.checkpoint["set_categories"]:
            idx = 0
            for section, characteristics in self.content['menu'].items():

                if characteristics['categorizable']:
                    categories_promt = f"""
                    Escribe como un Experto SEO
                    10 categorias relevantes para la seccion de {section} de una {self.store}.
                    En formato de lista de python. solo la lista de python.
                    siguiendo el siguiente formato: [categoria1, categoria2]
                    """
                    categories_response = get_completion(categories_promt)
                    categories_list = eval(categories_response)
                    characteristics["categorias"] = []
                    for category in categories_list:
                        characteristics["categorias"].append({
                            "name": category
                        })
                print(idx+1, "category set")
                idx += 1
            self.checkpoint["set_categories"] = 1
            self.save_content()
            self.save_checkpoint()

        print("Completed ✓\n")

    def set_subcategories(self):
        print("\n-------SUBCATEGORIES SET-------")
        section_idx = self.checkpoint["set_subcategories"]["section_idx"]
        category_idx = self.checkpoint["set_subcategories"]["category_idx"]
        idx = self.checkpoint["set_subcategories"]["idx"]
        for section, characteristics in list(self.content['menu'].items())[section_idx:]:
            if characteristics['categorizable']:

                for category in characteristics["categorias"][category_idx:]:
                    subcategories_prompt = f"""
                    Escribe como un Experto SEO
                    10 Subcategorias relevantes para la categoria de "{category["name"]}" de la seccion de "{section}" de una {self.store}.
                    En formato de lista de python. solo la lista de python.
                    siguiendo el siguiente formato: [subcategoria1, subcategoria2]
                    """
                    subcategories_response = get_completion(subcategories_prompt)
                    subcategories_list = eval(subcategories_response)
                    category["subcategorias"] = []
                    for subcategory in subcategories_list:
                        category["subcategorias"].append({
                            "name": subcategory
                        })
                    print(idx+1, "subcategory set")
                    idx += 1
                    category_idx += 1
                    self.checkpoint["set_subcategories"]["category_idx"] = category_idx
                    self.checkpoint["set_subcategories"]["idx"] = idx
                    self.save_checkpoint()
                    self.save_content()
                category_idx = 0
                self.checkpoint["set_subcategories"]["category_idx"] = category_idx
                self.save_checkpoint()

            section_idx += 1
            self.checkpoint["set_subcategories"]["section_idx"] = section_idx
            self.save_checkpoint()
        print("Completed ✓\n")

    def set_products(self):
        print("\n-------PRODUCTS SET-------")
        category_idx = self.checkpoint["set_products"]["category_idx"]
        subcategory_idx = self.checkpoint["set_products"]["subcategory_idx"]
        idx = self.checkpoint["set_products"]["idx"]

        if self.content['menu']['productos']:
            for category in self.content['menu']['productos']['categorias'][category_idx:]:
                for subcategory in category['subcategorias'][subcategory_idx:]:
                    products_prompt = f"""
                    Escribe como un Experto en la Busqueda de {self.products} en Amazon.
                    20 productos relevantes para la subcategoria de "{subcategory["name"]}" de la categoria de "{category["name"]}" de  la seccion de "productos"  de una {self.store}. 
                    
                    Asegurate de que sean productos que puedan encontrarse en Amazon.
                    
                    En formato de lista de python. solo la lista de python.
                    siguiendo el siguiente formato: [producto1, producto2]
                    """
                    products_response = get_completion(products_prompt)
                    products_list = eval(products_response)
                    subcategory["productos"] = products_list
                    print(idx+1, "subcategory products set")
                    idx += 1
                    subcategory_idx += 1
                    self.checkpoint["set_products"]["subcategory_idx"] = subcategory_idx
                    self.checkpoint["set_products"]["idx"] = idx
                    self.save_checkpoint()
                    self.save_content()
                subcategory_idx = 0
                self.checkpoint["set_products"]["subcategory_idx"] = subcategory_idx
                self.save_checkpoint()

                category_idx += 1
                self.checkpoint["set_products"]["category_idx"] = category_idx
                self.save_checkpoint()

        print("Completed ✓\n")

    def set_blog(self):
        print("\n-------BLOG SET-------")
        category_idx = self.checkpoint["set_blog"]["category_idx"]
        subcategory_idx = self.checkpoint["set_blog"]["subcategory_idx"]
        idx = self.checkpoint["set_blog"]["idx"]

        if self.content['menu']['blog']:
            for category in self.content['menu']['blog']['categorias'][category_idx:]:
                for subcategory in category['subcategorias'][subcategory_idx:]:
                    topics_prompt = f"""
                            Escribe como un Experto en SEO.
                            10 temas relevantes para la subcategoria de "{subcategory["name"]}" de la categoria de "{category["name"]}" de  la seccion de "blog"  de una {self.store}. 
                            En formato de lista de python. solo la lista de python.
                            siguiendo el siguiente formato: [tema1, tema2]
                            """
                    topics_response = get_completion(topics_prompt)
                    topics_list = eval(topics_response)
                    subcategory["temas"] = topics_list
                    print(idx + 1, "subcategory topics set")
                    idx += 1
                    subcategory_idx += 1
                    self.checkpoint["set_blog"]["subcategory_idx"] = subcategory_idx
                    self.checkpoint["set_blog"]["idx"] = idx
                    self.save_checkpoint()
                    self.save_content()
                subcategory_idx = 0
                self.checkpoint["set_blog"]["subcategory_idx"] = subcategory_idx
                self.save_checkpoint()

                category_idx += 1
                self.checkpoint["set_blog"]["category_idx"] = category_idx
                self.save_checkpoint()

        print("Completed ✓\n")

    def set_homepage(self):
        print("\n-------HOMEPAGE SET-------")
        homepage_prompt = """
        Escribe como un Experto SEO
        un articulo relevante e interesante sobre %s en general (3500 palabras).
        En formato JSON. solo el JSON.
         siguiendo el siguiente formato: 
        {
        "titulo": nombre del titulo,
        "meta-descripcion": meta descripcion en formato HTML,
        "contenido": contenido del articulo en formato HTML,
        }
        """ % self.products

        homepage_response = get_completion(homepage_prompt)
        homepage_dict = json.loads(homepage_response)
        self.content["menu"]["inicio"]["articulo"] = homepage_dict
        print("Completed ✓\n")

    def get_current_content(self):
        return self.content

    def load_checkpoint(self):
        try:
            with open('checkpoint.json', 'r') as file:
                self.checkpoint = json.load(file)
        except FileNotFoundError:
            self.save_checkpoint()

    def save_checkpoint(self):
        with open('checkpoint.json', 'w') as file:
            json.dump(self.checkpoint, file)

    def load_content(self):
        try:
            with open('content.json', 'r') as file:
                self.content = json.load(file)
        except FileNotFoundError:
            self.save_content()

    def save_content(self):
        with open('content.json', 'w') as file:
            json.dump(self.content, file)

