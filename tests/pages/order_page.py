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

    PAYMENT_RADIO = (By.CSS_SELECTOR, ".payment-option label")
    TERMS_CHECKBOX = (By.CSS_SELECTOR, "input[name='conditions_to_approve[terms-and-conditions]']")
    PLACE_ORDER_BUTTON = (By.CSS_SELECTOR, "#payment-confirmation button[type='submit']")

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

    def choose_payment_and_confirm(self):
        payment_labels = self.wait_find_elements(self.PAYMENT_RADIO)
        random_payment = random.choice(payment_labels)
        random_payment.click()
        checkbox_input = self.wait_find_element(self.TERMS_CHECKBOX)
        checkbox_input.click()
        self.click(self.PLACE_ORDER_BUTTON)