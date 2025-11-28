from pages.cart_page import CartPage
from pages.order_page import OrderPage
from selenium.webdriver.support.ui import WebDriverWait



def test_make_payment(driver):
    cart = CartPage(driver)
    cart.open_order()

    order = OrderPage(driver)
    order.fill_address(
        firstname="Test",
        lastname="User",
        address="10 Downing Street",
        postal="80-111",
        city="London",
        country="United Kingdom",
        phone="07123456789"
    )

    order.choose_shipping()

    order.choose_payment_and_confirm()

    WebDriverWait(driver, 10).until(lambda d: "/potwierdzenie-zamowienia" in d.current_url)
    assert "/potwierdzenie-zamowienia" in driver.current_url