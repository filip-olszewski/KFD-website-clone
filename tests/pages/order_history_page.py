from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class OrderHistoryPage(BasePage):

    URL = "http://localhost:8080/order-history"
    ORDER_TABLE = (By.CSS_SELECTOR, "table.table tbody tr")
    STATUS_COLUMN = (By.CSS_SELECTOR, "td:nth-child(5) span.label")

    def open(self):
        self.driver.get(self.URL)

    def get_order_status(self):
        first_row = self.wait_to_appear(self.ORDER_TABLE)
        status_element = first_row.find_element(*self.STATUS_COLUMN)
        return status_element.text.strip()