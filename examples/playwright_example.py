from playwright.sync_api import sync_playwright

from chopperfix.chopper_decorators import chopperdoc


class CustomPlaywright:
    def __init__(self, timeout=10000, retry_attempts=1):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(timeout)
        self.retry_attempts = retry_attempts

    @chopperdoc
    def perform_action(self, action, **kwargs):
        for attempt in range(self.retry_attempts):
            try:
                if action == 'click':
                    self.page.click(kwargs['selector'])
                elif action == 'navigate':
                    self.page.goto(kwargs.get('url', ''))
                return True
            except Exception as e:
                print(f"Intento {attempt + 1} fallido: {e}")
                if attempt == self.retry_attempts - 1:
                    raise

    def click(self, selector):
        return self.perform_action('click', selector=selector)

    def navigate(self, url):
        return self.perform_action('navigate', url=url)

    def close(self):
        self.browser.close()
        self.playwright.stop()

# Prueba del decorador y self-healing con Playwright
driver = CustomPlaywright()
driver.navigate('https://example.com')
driver.click(selector='invalid_selector')  # Este selector fallará y activará el self-healing
driver.close()
