from .base_page import BasePage

class RegisterPage(BasePage):
   
    def open_register(self):
        self.open("http://localhost:8080/login?create_account=1")