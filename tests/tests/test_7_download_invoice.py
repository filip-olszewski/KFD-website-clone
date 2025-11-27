from pages.order_history_page import OrderHistoryPage


def test_download_invoice(driver):
    history = OrderHistoryPage(driver)
    history.open()
    href = history.download_pdf()
    assert "controller=pdf-invoice" in href, f"Link nie prowadzi do faktury PDF: {href}"
