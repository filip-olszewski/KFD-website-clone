from .base_page import BasePage
from selenium.webdriver.common.by import By
import random


class OrderPage(BasePage):
    ADDRESS = (By.ID, "field-address1")
    POSTAL = (By.ID, "field-postcode")
    CITY = (By.ID, "field-city")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "button[name='confirm-addresses']")

    SHIPPING_RADIO = (By.CSS_SELECTOR, ".delivery-option.js-delivery-option label.delivery-option-2")
    CONTINUE_SHIPPING = (By.NAME, "confirmDeliveryOption")

    def fill_address(self, firstname, lastname, address, postal, city, country, phone):
        self.type(self.ADDRESS, address)
        self.type(self.POSTAL, postal)
        self.type(self.CITY, city)
        self.click(self.CONTINUE_BUTTON)

    def choose_shipping(self):
        labels = self.wait_find_elements(self.SHIPPING_RADIO)
        random_label = random.choice(labels)
        random_label.click()
        self.click(self.CONTINUE_SHIPPING)