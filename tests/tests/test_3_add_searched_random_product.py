from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_page import SearchPage
from pages.cart_page import CartPage


def test_add_random_product(driver):
    home = HomePage(driver)
    product = ProductPage(driver)
    search = SearchPage(driver)
    cart = CartPage(driver)

    home.open_home()
    home.search("krem") # to change
    initial = cart.get_amount_of_products()
    search.open_random_product()
    product.add_to_cart()
    product.continue_shopping()
    home.open_cart()

    assert initial < cart.get_amount_of_products()
    
