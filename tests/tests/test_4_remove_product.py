from pages.home_page import HomePage
from pages.cart_page import CartPage

def test_remove_3_products(driver):
    home = HomePage(driver)
    cart = CartPage(driver)

    home.open_cart()
    initial_count = cart.get_len_of_cart()
    cart.remove_random_items(3)
    final_count = cart.get_len_of_cart()
    assert final_count == initial_count - 3