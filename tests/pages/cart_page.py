from selenium.webdriver.common.by import By

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