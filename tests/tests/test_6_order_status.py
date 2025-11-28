from pages.order_history_page import OrderHistoryPage

statuses = [
    "Płatność zaakceptowana",
    "Przygotowanie w toku",
    "Wysłane",
    "Dostarczone",
    "Zwróconych pieniędzy",
    "Zamówienie oczekujące (opłacone)",
    "Płatność przyjęta"
]

def test_order_status(driver):
    history = OrderHistoryPage(driver)
    history.open()
    status = history.get_order_status()
    assert status in statuses