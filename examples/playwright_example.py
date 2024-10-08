from playwright.sync_api import sync_playwright

from chopperfix.chopper_decorators import action_logger


class CustomPlaywright:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)  # Abre el navegador en modo visible
        self.page = self.browser.new_page()

    @action_logger
    def click(self, selector):
        self.page.click(selector)

    @action_logger
    def navigate(self, url):
        self.page.goto(url)

    def close(self):
        self.browser.close()
        self.playwright.stop()

# Prueba del decorador y self-healing con Playwright
driver = CustomPlaywright()
driver.navigate('https://example.com')
driver.click(selector='invalid_selector')  # Este selector fallará y activará el self-healing
driver.close()
