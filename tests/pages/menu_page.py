from selenium.webdriver.common.by import By
from .base_page import BasePage

class MenuPage(BasePage):

    CATEGORY_LINKS = (By.CSS_SELECTOR, "#_desktop_top_menu a.dropdown-item") # to change (probably)

    def open_category(self, name):
        links = self.driver.find_elements(*self.CATEGORY_LINKS)

        for link in links:
            if link.text.strip().lower() == name.lower():
                link.click()
                return

        raise Exception(f"Category '{name}' not found")

    def open_category_by_partial(self, part):
        links = self.driver.find_elements(*self.CATEGORY_LINKS)

        for link in links:
            if part.lower() in link.text.strip().lower():
                link.click()
                return

        raise Exception(f"Category containing '{part}' not found")