from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def click(self, locator, use_js=False):
        element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
        if use_js:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            element.click()

    def type(self, locator, text):
        element = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def find(self, locator):
        return WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))