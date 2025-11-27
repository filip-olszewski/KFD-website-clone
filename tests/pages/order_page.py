from .base_page import BasePage
from selenium.webdriver.common.by import By


class OrderPage(BasePage):
    ADDRESS = (By.ID, "field-address1")
    POSTAL = (By.ID, "field-postcode")
    CITY = (By.ID, "field-city")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "button[name='confirm-addresses']")

    def fill_address(self, firstname, lastname, address, postal, city, country, phone):
        self.type(self.ADDRESS, address)
        self.type(self.POSTAL, postal)
        self.type(self.CITY, city)
        self.click(self.CONTINUE_BUTTON)