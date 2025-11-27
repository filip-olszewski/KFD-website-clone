from .base_page import BasePage
from selenium.webdriver.common.by import By

class RegisterPage(BasePage):
    GENDER_MR = (By.ID, "field-id_gender-1")
    GENDER_MRS = (By.ID, "field-id_gender-2")
    GENDER_MR_LABEL = (By.CSS_SELECTOR, "label[for='field-id_gender-1']")
    GENDER_MRS_LABEL = (By.CSS_SELECTOR, "label[for='field-id_gender-2']")

    FIRSTNAME = (By.ID, "field-firstname")
    LASTNAME = (By.ID, "field-lastname")
    EMAIL = (By.ID, "field-email")
    PASSWORD = (By.ID, "field-password")
    BIRTHDATE = (By.ID, "field-birthday")

    CUSTOMER_PRIVACY = (By.NAME, "customer_privacy")
    TERMS = (By.NAME, "psgdpr")
    CUSTOMER_PRIVACY_LABEL = (By.CSS_SELECTOR, "input[name='customer_privacy'] + span")
    TERMS_LABEL = (By.CSS_SELECTOR, "input[name='psgdpr'] + span")
    NEWSLETTER = (By.NAME, "newsletter")
    OPTIN = (By.NAME, "optin")
    NEWSLETTER_LABEL = (By.CSS_SELECTOR, "input[name='newsletter'] + span")
    OPTIN_LABEL = (By.CSS_SELECTOR, "input[name='optin'] + span")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success") 
            
    def open_register(self):
        self.open("http://localhost:8080/login?create_account=1")

    def register(self, gender="Mr", firstname="", lastname="", email="", password="", birthdate="", newsletter=False, optin=False):
        if gender.lower() == "mr":
            self.click(self.GENDER_MR_LABEL)
        else:
            self.click(self.GENDER_MRS_LABEL)
        self.type(self.FIRSTNAME, firstname)
        self.type(self.LASTNAME, lastname)
        self.type(self.EMAIL, email)
        self.type(self.PASSWORD, password)
        
        if birthdate:
            self.type(self.BIRTHDATE, birthdate)
        
        self.click(self.CUSTOMER_PRIVACY_LABEL, use_js=True)
        self.click(self.TERMS_LABEL, use_js=True)

        if newsletter:
            self.click(self.NEWSLETTER_LABEL, use_js=True)
        if optin:
            self.click(self.OPTIN_LABEL, use_js=True)
        
        self.click(self.SUBMIT_BUTTON)