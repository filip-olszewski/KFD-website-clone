from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

from .base_page import BasePage

class CartPage(BasePage):

    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item")
    REMOVE_BUTTONS = (By.CSS_SELECTOR, ".remove-from-cart")
    LOADING_OVERLAY = (By.CSS_SELECTOR, ".cart-overview") 
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, ".checkout a.btn.btn-primary")
    CART_AMOUNT = (By.CSS_SELECTOR, ".cart-products-count")

    def open_order(self):
        self.click(self.CHECKOUT_BUTTON)

    def get_items(self):
        return self.driver.find_elements(*self.CART_ITEMS)
    
    def get_len_of_cart(self):
        return len(self.get_items())
    
    def remove_item_by_index(self, index):
        buttons = self.driver.find_elements(*self.REMOVE_BUTTONS)
        buttons[index].click()

        # It's needed cuz PrestaShop deletes elements from cart with ajax
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(buttons[index])
        )

    def remove_random_items(self, count):
        for _ in range(count):
            items = self.get_items()
            if not items:
                break
            random_index = random.randint(0, len(items) - 1)
            self.remove_item_by_index(random_index)