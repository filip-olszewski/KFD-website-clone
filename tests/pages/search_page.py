from selenium.webdriver.common.by import By
from .base_page import BasePage
import random

class SearchPage(BasePage):

    PRODUCTS = (By.CSS_SELECTOR, "article.product-miniature a.product-thumbnail") # to change (probably)

    def get_products(self):
        return self.driver.find_elements(*self.PRODUCTS)

    def open_random_product(self):
        items = self.get_products()
        if not items:
            raise Exception("No products")
        random.choice(items).click()