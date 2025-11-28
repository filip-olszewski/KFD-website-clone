from selenium.webdriver.common.by import By
from .base_page import BasePage
import random

class CategoryPage(BasePage):

    PRODUCTS = (By.CSS_SELECTOR, "article.product-miniature a.product-thumbnail") # to change (probably)

    def open_product_by_index(self, index):
        items = self.driver.find_elements(*self.PRODUCTS)
        items[index].click()

    def open_random_product(self):
        items = self.driver.find_elements(*self.PRODUCTS)
        random.choice(items).click()

    def count_products(self):
        return len(self.driver.find_elements(*self.PRODUCTS))
