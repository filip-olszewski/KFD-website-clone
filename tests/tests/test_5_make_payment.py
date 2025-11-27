from pages.cart_page import CartPage
from pages.order_page import OrderPage


def test_make_payment(driver):
    cart = CartPage(driver)
    cart.open_order()

    order = OrderPage(driver)
    order.fill_address(
        firstname="Test",
        lastname="User",
        address="10 Downing Street",
        postal="SW1A 2AA",
        city="London",
        country="United Kingdom",
        phone="07123456789"
    )