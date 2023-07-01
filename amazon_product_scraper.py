import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.request import urlretrieve
import lxml
import pprint
import os
import difflib
from PIL import Image
import spacy
from sklearn.metrics.pairwise import cosine_similarity

# Selenium web driver Options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode (optional)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set the download directory
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "/path/to/download/directory",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


def process_images(input_directory, output_directory, crop_width, crop_height):
    # Iterate through all files in the input directory
    for filename in os.listdir(input_directory):
        # Construct the input and output paths for each image
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)

        # Open the image
        image = Image.open(input_path)

        # Check if the image has an alpha channel
        if image.mode != 'RGBA':
            # Convert the image to RGBA mode
            image = image.convert('RGBA')

        # Create a new image with an alpha channel
        new_image = Image.new('RGBA', image.size, (0, 0, 0, 0))

        # Composite the original image onto the new image
        new_image.paste(image, (0, 0), mask=image)

        # Get the dimensions of the image
        width, height = new_image.size

        # Calculate the aspect ratio of the image
        aspect_ratio = width / height

        # Calculate the target aspect ratio for cropping
        target_aspect_ratio = crop_width / crop_height

        # Calculate the crop box dimensions
        if aspect_ratio > target_aspect_ratio:
            # Image is wider, adjust height
            new_height = int(width / target_aspect_ratio)
            top = (height - new_height) // 2
            bottom = top + new_height
            left = 0
            right = width
        else:
            # Image is taller, adjust width
            new_width = int(height * target_aspect_ratio)
            left = (width - new_width) // 2
            right = left + new_width
            top = 0
            bottom = height

        # Crop the image
        cropped_image = new_image.crop((left, top, right, bottom))

        # Resize the cropped image to the desired dimensions
        resized_image = cropped_image.resize((crop_width, crop_height))

        # Save the cropped and resized image as PNG to preserve transparency
        resized_image.save(output_path, format='WebP')


def check_title_description_fit(title, description, threshold=0.8):
    # Load the spaCy model
    nlp = spacy.load('en_core_web_sm')

    # Tokenize and vectorize the texts
    title_vector = nlp(title).vector
    description_vector = nlp(description).vector

    # Calculate the cosine similarity
    similarity = cosine_similarity(title_vector.reshape(1, -1), description_vector.reshape(1, -1))[0][0]

    # Determine if the title fits the description
    if similarity >= threshold:
        return True
    else:
        return False


class AmazonProductScraper:

    def __init__(self, driver_path, username, password):
        ser = Service(driver_path)
        self.driver = webdriver.Chrome(options=chrome_options, service=ser)
        self.driver.get("https://www.amazon.com.mx/ref=nav_logo")
        # Here define de max seconds driver will wait for an element
        self.wait = WebDriverWait(self.driver, 5)
        self.username = username
        self.password = password

    def get_post_image(self, title, download_image_path):
        self.driver.get(f"https://www.google.com/search?q={title}&tbm=isch&hl=en-US&tbs=isz:l%2Cil:cl&sa=X&ved=0CAIQpwVqFwoTCMDZgf6v7P8CFQAAAAAdAAAAABAC&biw=1905&bih=912")
        image_frame = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')))
        image_frame.click()
        product_image = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]')))
        image_path = f"{download_image_path}{title}.jpg"
        image_url = product_image.get_attribute("src")
        urlretrieve(image_url, image_path)
        return image_path

    def login(self):
        signin_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="nav-signin-tooltip"]/a')))
        signin_button.click()

        username_field = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="ap_email"]')))
        username_field.send_keys(self.username)

        continue_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="continue"]')))
        continue_button.click()

        password_field = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="ap_password"]')))
        password_field.send_keys(self.password)

        signin_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="signInSubmit"]')))
        signin_button.click()

    def search_product(self, product, download_image_path):
        self.driver.get("https://www.amazon.com.mx/ref=nav_logo")
        try:
            # Here waits in case you need to introduce captcha
            search_field = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="twotabsearchtextbox"]')))
            search_field.send_keys("")
            print(product)
            search_field.send_keys(f'{product}')

            search_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="nav-search-submit-button"]')))
            search_button.click()
            try:
                best_choice = self.select_best_option(product)
                idx = best_choice['element'].get('data-index')
                title = best_choice['title']
            except ValueError:
                return "", "", ""

            product_frame = self.wait.until(
                EC.visibility_of_element_located((By.XPATH,
                                                  f'//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{idx if idx else 0}]/div/div/div/div[1]')))

            product_frame.click()
            product_image = self.wait.until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'a-dynamic-image')))
            image_path = f"{download_image_path}{product}.jpg"
            image_url = product_image.get_attribute("src")
            urlretrieve(image_url, image_path)

            text_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="amzn-ss-text-link"]')))
            text_button.click()

            url_textarea = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="amzn-ss-text-shortlink-textarea"]')))

            url_text = url_textarea.get_attribute("value")

            return title, url_text, image_path
        except TimeoutException:
            print('Time to wait for the element finish, jumped to the next one')
            return "", "", ""

    def select_best_option(self, product_name):
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        search = soup.find("div", class_="s-main-slot")
        all_product_options = search.findAll('div', class_="s-result-item")
        chosen_products = []

        for element in all_product_options[1:7]:
            try:

                title = element.find('span', class_="a-size-base-plus")
                root = element.find('div', class_="a-size-small")
                reviews = root.find_all('span', attrs={'aria-label': True})[1]

                if check_title_description_fit(title.get_text().lower(), element.get_text().lower()):

                    excluded_chars = ','
                    product = {
                        'title': title.text,
                        'reviews': int(''.join(char for char in reviews.text if char not in excluded_chars)),
                        'element': element
                    }

                    chosen_products.append(product)

            except AttributeError:
                print("This product doesn't exist")
        best_choice = max(chosen_products, key=lambda x: x['reviews'])

        return best_choice if best_choice else {}

    def get_products_data(self):
        return self.data

    def process_images(self, download_image_path):
        process_images(download_image_path, download_image_path, 1200, 675)

    def delete_all_images(self, download_image_path):
        # Iterate through all files in the directory
        for filename in os.listdir(download_image_path):
            # Construct the file path
            file_path = os.path.join(download_image_path, filename)

            # Check if the file is an image (adjust the image file extensions as per your requirements)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Delete the image file
                os.remove(file_path)
