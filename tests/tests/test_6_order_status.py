from pages.order_history_page import OrderHistoryPage

statuses = [
    "awaiting check payment",
    "payment accepted",
    "processing in progress",
    "shipped",
    "delivered",
    "cancled",
    "refunded",
    "payment error",
    "on backorder (paid)",
    "awaiting bank wire payment",
    "remote payment accepted",
    "on backorder (not paid)",
    "Awaiting cash on delivery validation",
    "waiting for payment",
    "partial refund",
    "partial payment",
    "authorized. to be captured by merchant",
    "waiting for confirmation",
    "waiting for package",
    "package received",
    "return denied",
    "return completed"
]

def test_order_status(driver):
    history = OrderHistoryPage(driver)
    history.open()
    status = history.get_order_status()
    assert status.lower() in statuses