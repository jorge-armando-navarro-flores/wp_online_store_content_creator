import requests
import os

products_to_upload = [{'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/3qJlyHb',
                       'title': 'Juego de utensilios de cocina de bambú.jpg'},
                      {'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/4687HdK',
                       'title': 'Tabla de cortar de madera de acacia.jpg'},
                      {'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/3N4YiuQ',
                       'title': 'Juego de recipientes de almacenamiento de vidrio.jpg'},
                      {'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/3pbzrxC',
                       'title': '"Pajitas de acero inoxidable reutilizables.jpg'},
                      {'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/443Axdv',
                       'title': 'Filtro de café reutilizable de acero inoxidable.jpg'},
                      {'image_path': '/home/jorge/Development/wp_amazon_product_gallery_uploader/product_images/',
                       'ref_url': 'https://amzn.to/4452AsZ',
                       'title': 'Envolturas de cera de abeja reutilizables.jpg'}]


class ContentUploader:

    def __init__(self, username, password, site_url):
        self.auth = (username, password)
        self.site_url = site_url

    def new_page_with_gallery(self, title, products, article):
        url = self.site_url + 'wp-json/wp/v2/pages'
        content = article["meta-descripcion"] + \
                  self.create_gallery(products) + \
                  '<h2>Ventajas</h2>' + \
                  article["ventajas"] + \
                  '<h2>Preguntas Frecuentes</h2>' + \
                  article["preguntas-frecuentes"]
        data = {
            'title': title,
            'content': content,
            'status': "publish"
        }
        response = requests.post(url, auth=self.auth, json=data)

        # Check the response from the WordPress API
        if response.status_code == 201:
            page_id = response.json().get('id')
            print('The new page has been created successfully. Page ID:', page_id)
        else:
            print('Error creating the new page. Status code:', response.status_code)
            print('Error message:', response.text)

    def append_gallery_to_a_page(self, page_name):
        # Define the URL of the WordPress API and the endpoint to retrieve/update a page
        url = self.site_url + 'wp-json/wp/v2/pages/{page_id}'  # Replace with your site's URL
        page_name = "-".join(page_name.lower().split())
        print("PAGE NAME", page_name)
        page_id = self.get_page_id_by_name(page_name)

        # Retrieve the current content of the page
        response = requests.get(url.format(page_id=page_id), auth=self.auth)

        # Check the response from the WordPress API
        if response.status_code == 200:
            page_data = response.json()
            current_content = page_data['content']['rendered']
            new_content = current_content + self.create_gallery()  # Modify the content as needed

            # Update the page with the modified content
            data = {
                'content': new_content
            }

            update_response = requests.post(url.format(page_id=page_id), auth=self.auth, json=data)

            # Check the response from the WordPress API
            if update_response.status_code == 200:
                print('Page updated successfully.')
            else:
                print('Error updating the page. Status code:', update_response.status_code)
                print('Error message:', update_response.text)
        else:
            print('Error retrieving the page. Status code:', response.status_code)
            print('Error message:', response.text)

    def get_page_id_by_name(self, page_name):
        # Define the URL of the WordPress API and the endpoint to fetch pages
        url = self.site_url + 'wp-json/wp/v2/pages'  # Replace with your site's URL

        # Make a GET request to fetch all pages
        response = requests.get(url, auth=self.auth)

        # Check the response from the WordPress API
        if response.status_code == 200:
            pages = response.json()

            # Search for the page by name and retrieve its ID
            page_id = None
            for page in pages:
                print(page)
                if page['slug'] == page_name:
                    page_id = page['id']
                    break

            if page_id is not None:
                return page_id
            else:
                print('Page not found.')
        else:
            print('Error retrieving pages. Status code:', response.status_code)
            print('Error message:', response.text)
        return 0

    def upload_image(self, image_path):
        url = self.site_url + 'wp-json/wp/v2/media'
        image = image_path
        with open(image, 'rb') as file:
            headers = {
                f'Content-Disposition': f'attachment; filename="{image_path.split("/")[-1]}"',
                'Content-Type': 'image/jpeg'
            }
            response = requests.post(url, auth=self.auth, headers=headers, data=file)

            if response.status_code == 201:
                return response.json().get('id')
            else:
                print('Error uploading image:', image)
                print('Status code:', response.status_code)
                print('Error message:', response.text)
                return ""

    def create_gallery(self, products):
        gallery_content = '<div class="container">'

        for product in products:
            if product["ref_url"]:
                image_url = self.get_image_url(product["image_id"])
                gallery_content += '<div class="product"> \
                                          <img src="%s" alt="%s"> \
                                          <div class="details"> \
                                              <h3>%s</h3> \
                                              <p>%s</p> \
                                              <a href="%s" target="_blank" rel="nofollow" class="buy-btn">Comprar en Amazon</a> \
                                          </div> \
                                    </div>' % (image_url,  product["titulo"], f"{product['titulo'][:30]}..", product["nombre"], product["ref_url"])
        gallery_content += '</div>'

        return gallery_content

    def get_image_url(self, image_id):
        url = self.site_url + 'wp-json/wp/v2/media/%s' % image_id

        # Make a GET request to fetch the image information
        response = requests.get(url)

        # Check the response from the WordPress API
        if response.status_code == 200:
            image_data = response.json()
            if isinstance(image_data, dict):
                image_url = image_data['guid']['rendered']
            elif isinstance(image_data, list):
                image_url = image_data[0]['guid']['rendered']
        else:
            print('Error retrieving the image URL. Status code:', response.status_code)
            print('Error message:', response.text)
            image_url = image_id

        print(image_url)
        return image_url