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

    def start_content_structure(self):
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

    def set_categories(self):
        for section, caracteristics in self.content['menu'].items():

            if caracteristics['categorizable']:
                categories_promt = f"""
                Escribe como un Experto SEO
                10 categorias relevantes para la seccion de {section} de una {self.store}.
                En formato de lista de python. solo la lista de python.
                siguiendo el siguiente formato: [categoria1, categoria2]
                """
                categories_response = get_completion(categories_promt)
                categories_list = eval(categories_response)
                caracteristics["categorias"] = []
                for category in categories_list:
                    caracteristics["categorias"].append({
                        "name": category
                    })
            print("category set")


    def set_subcategories(self):
        for section, caracteristics in self.content['menu'].items():
            if caracteristics['categorizable']:
                for category in caracteristics["categorias"]:
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
            print("subcategory set")

    def set_products(self):
        if self.content['menu']['productos']:
            for category in self.content['menu']['productos']['categorias']:
                for subcategory in category['subcategorias']:
                    products_prompt = f"""
                    Escribe como un Experto SEO
                    20 productos relevantes para la subcategoria de "{subcategory["name"]}" de la categoria de "{category["name"]}" de  la seccion de "productos"  de una {self.store}. 
                    
                    Asegurate de que sean productos que puedan encontrarse en Amazon.
                    
                    En formato de lista de python. solo la lista de python.
                    siguiendo el siguiente formato: [producto1, producto2]
                    """
                    products_response = get_completion(products_prompt)
                    products_list = eval(products_response)
                    subcategory["products"] = products_list
                    print("subcategory products set")





    def get_current_content(self):
        return self.content

