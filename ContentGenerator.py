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
    def __init__(self, store_name, products):
        self.store_name = store_name
        self.products = products
        self.content = {}

    def get_relevant_categories(self):
        prompt = f"""
            categorias reelevantes para una tienda de {self.products}  que vende productos que se encuentran en amazon
            sin saltos de linea una sola linea    
        """
        response = get_completion(prompt)
        return response

    def start_content_structure(self):
        prompt = f"""
            Instrucciones:
            Escribe como un experto en contenidos de calidad, persuasivos y optimizados para motores de busqueda para tiendas en linea.
            Este es un diccionario que representa una tienda en línea de productos ecológicos y sostenibles. Tu objetivo es proporcionar la estructura del diccionario en formato JSON, incluyendo la mayor cantidad de secciones y categorías relevantes que puedas pensar para la tienda. Recuerda que la tienda se enfoca en vender productos que están disponibles en Amazon.
            
            Por favor, crea la estructura del diccionario en formato JSON, solo el JSON, siguiendo las siguientes especificaciones:
            
            - El diccionario principal se llama "{self.store_name}".
            - Dentro de "tienda_ecologica", agrega una clave llamada "Secciones" que contiene otro diccionario.
            - Cada sección debe ser una clave dentro del diccionario "Secciones".
            - Para cada sección, incluye las siguientes claves:
                - "Descripción": Una breve descripción de dos líneas sobre la sección.
                - "Categorías": Un diccionario anidado que representa las categorías disponibles dentro de esa sección.
            - Dentro de cada categoría, incluye las siguientes claves:
                - "Descripción": Una breve descripción de dos líneas sobre la categoría.
            
            Utiliza tu criterio y conocimiento para determinar las secciones y categorías relevantes para una tienda 
            en línea de productos ecológicos y sostenibles que se enfoque en vender productos disponibles en Amazon. 
            Aquí tienes algunos ejemplos de secciones y categorías que podrías considerar: 
            {self.get_relevant_categories()}, entre otros.
            
            Agrega la mayor cantidad posible de secciones y categorías relevantes, proporcionando descripciones breves de dos líneas para cada sección y categoría que agregues.
            Solo dame el JSON
        """
        response = get_completion(prompt)
        self.content = json.loads(response)

    def set_section_categories(self):
        sections = list(self.content['tienda_ecologica']['Secciones'].keys())

        for section in sections[:2]:
            categories = list(self.content['tienda_ecologica']['Secciones'][section]['Categorías'].keys())
            for category in categories[:2]:
                prompt = f"""
                    Instrucciones:
                    Escribe como un experto en contenidos de calidad, persuasivos y optimizados para motores de busqueda para tiendas en linea.
                    Este es un diccionario que representa una tienda en línea de {self.products} en la seccion de "{section}" dentro la categoria de "{category}". Contiene información sobre la categoria, descripcion, ventajas, preguntas frecuentes, y productos disponibles en la tienda. Tu objetivo es proporcionar la estructura del diccionario en formato JSON, incluyendo la mayor cantidad de ventajas, preguntas frecuentes, y productos relevantes que puedas pensar para la categoria. Recuerda que la tienda se enfoca en vender productos que están disponibles en Amazon.
                    
                    Por favor, crea la estructura del diccionario en formato JSON, solo el JSON, siguiendo las siguientes especificaciones:
                    
                    - El diccionario principal se llama "categoria_tienda_ecologica".
                    - Dentro de "categoria_tienda_ecologica", se deben incluir las siguientes claves:
                        - "Ventajas": Una lista que contiene las ventajas bien desarrolladas de los productos de esa categoría con el formato "ventaja: desarrollo".
                        - "Preguntas frecuentes": Una lista que contiene las preguntas frecuentes que los posibles compradores podrían hacer sobre los productos de esa categoría y sus respuestas.
                        - "Descripción": Una breve descripción de dos líneas sobre la categoría.
                        - "Productos": Una lista que contiene ejemplos de productos relacionados con esa categoría. Asegúrate de que los productos mencionados sean productos que podrían encontrarse en Amazon.
                        
                    Utiliza tu criterio y conocimiento para determinar las ventajas, preguntas frecuentes y productos relevantes para una tienda en línea de {self.products} en la seccion de {section} dentro la categoria de {category} que se enfoque en vender productos disponibles en Amazon.
                    
                    Agrega la mayor cantidad posible de ventajas, preguntas frecuentes y productos.
                    
                    Las ventajas deben estar bien desarrolladas y con el formato "ventaja: desarrollo"
                    Los productos deben ser 15 o mas, Recuerda que deben ser productos que podrian encontrarse en Amazon.
                """
                response = get_completion(prompt)
                category_params = json.loads(response)
                self.content['tienda_ecologica']['Secciones'][section]['Categorías'][category].update(category_params['categoria_tienda_ecologica'])
                print(f"Section: {section} category: {category} UPDATED")


    def get_current_content(self):
        return self.content

