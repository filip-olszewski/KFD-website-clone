from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from.base_page import BasePage

class HomePage(BasePage):
    SEARCH_INPUT = (By.NAME, "s")
    CART_BUTTON = (By.CSS_SELECTOR, "#_desktop_cart")
    CART_COUNT = (By.CSS_SELECTOR, "#_desktop_cart .cart-products-count")
    CART_MODAL = (By.ID, "blockcart-modal")

    def open_home(self):
        self.open("http://localhost:8080")

    def search(self, text):
        field = self.find(self.SEARCH_INPUT)
        field.send_keys(text + Keys.ENTER)