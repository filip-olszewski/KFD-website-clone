from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from random import randint

class ProductPage(BasePage):

    ADD_TO_CART = (By.CSS_SELECTOR, "button.add-to-cart")
    QUANTITY_INPUT = (By.ID, "quantity_wanted")

    def add_to_cart(self):
        quantity_input = self.driver.find_element(*self.QUANTITY_INPUT)
        quantity_input.clear()
        self.driver.execute_script("arguments[0].value = arguments[1];", quantity_input, randint(1, 5)) # (1, 5) is custom value
        self.click(self.ADD_TO_CART)
