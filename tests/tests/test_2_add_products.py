from pages.menu_page import MenuPage
from pages.category_page import CategoryPage
from pages.product_page import ProductPage
from pages.home_page import HomePage
from pages.cart_page import CartPage

def test_add_10_products(driver):
    menu = MenuPage(driver)
    category = CategoryPage(driver)
    product = ProductPage(driver)
    home = HomePage(driver)
    cart = CartPage(driver)

    home.open_home()

    menu.open_category("Clothes") # here custom value is needed

    for i in range(2): # here also
        category.open_product_by_index(i)
        product.add_to_cart()
        product.continue_shopping()
        driver.get("http://localhost:8080/3-clothes") # here also

    driver.get("http://localhost:8080/6-accessories") # here also

    for i in range(8): # here also
        category.open_product_by_index(i)
        product.add_to_cart()
        product.continue_shopping()
        driver.get("http://localhost:8080/6-accessories") # here also

    home.open_cart()
    assert cart.get_len_of_cart() >= 10