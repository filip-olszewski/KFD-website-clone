import pytest
from pages.register_page import RegisterPage
from selenium.webdriver.support.ui import WebDriverWait
from faker import Faker

faker = Faker()

@pytest.mark.usefixtures("driver")
def test_register(driver):
    
    register = RegisterPage(driver)
    register.open_register()

    credentials = (
        "Mr",
        faker.first_name(),
        faker.last_name(),
        faker.unique.email(),
        "testing",
        faker.date_of_birth(minimum_age=18, maximum_age=60).strftime("%m/%d/%Y"),
        False,
        False,
    )

    register.register(*credentials)
    WebDriverWait(driver, 10).until(lambda d: "localhost:8080/" in d.current_url)
    assert "localhost:8080/login?create_account=1" != driver.current_url.lower(), "User was not redirected to home page after registration"