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
                elif action == 'type':
                    self.page.fill(kwargs['selector'], kwargs.get('text', ''))
                elif action == 'press':
                    self.page.press(kwargs['selector'], kwargs.get('key', ''))
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

    def type(self, selector, text):
        return self.perform_action('type', selector=selector, text=text)

    def press(self, selector, key):
        return self.perform_action('press', selector=selector, key=key)

    def close(self):
        self.browser.close()
        self.playwright.stop()

# Prueba del decorador y self-healing con un flujo extendido en Wikipedia
driver = CustomPlaywright()

# Navegar a la página principal de Wikipedia
driver.navigate('https://www.wikipedia.org')

# Intentar escribir en un selector inválido para activar el self-healing
driver.type(selector='#searchInputsfffsssss', text='One piece')

# Intentar presionar una tecla en un selector inválido para activar el self-healing
driver.press(selector='#searchInput', key='Enter')

# Cerrar el navegador
driver.close()

from learning.pattern_storage import PatternStorage

# Crear una instancia de PatternStorage
storage = PatternStorage()

# Recuperar los patrones usando el nuevo método
patterns = storage.get_all_patterns(limit=10)

# Imprimir los detalles de cada patrón
for pattern in patterns:
    print(f"Acción: {pattern.action}, Selector: {pattern.selector}, URL: {pattern.url}, "
          f"Timestamp: {pattern.timestamp}, Descripción: {pattern.description}, Peso: {pattern.peso}")