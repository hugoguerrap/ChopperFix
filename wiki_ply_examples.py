from playwright.sync_api import sync_playwright
from chopperfix.chopper_decorators import chopperdoc
from llm_integration.langchain_manager import LangChainManager


class CustomPlaywright:
    def __init__(self, timeout=5000, retry_attempts=1):
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
                    self.page.locator(kwargs['xpath']).click()
                elif action == 'type':
                    self.page.locator(kwargs['xpath']).fill(kwargs.get('text', ''))
                elif action == 'press':
                    self.page.locator(kwargs['xpath']).press(kwargs.get('key', ''))
                elif action == 'navigate':
                    self.page.goto(kwargs.get('url', ''))
                return True
            except Exception as e:
                print(f"Intento {attempt + 1} fallido: {e}")
                if attempt == self.retry_attempts - 1:
                    raise

    def click(self, xpath):
        return self.perform_action('click', xpath=xpath)

    def navigate(self, url):
        return self.perform_action('navigate', url=url)

    def type(self, xpath, text):
        return self.perform_action('type', xpath=xpath, text=text)

    def press(self, xpath, key):
        return self.perform_action('press', xpath=xpath, key=key)

    def close(self):
        self.browser.close()
        self.playwright.stop()


# Prueba del decorador y self-healing con un flujo extendido en Wikipedia
driver = CustomPlaywright()

# Navegar a la página principal de Wikipedia
driver.navigate('https://www.wikipedia.org')

# Intentar escribir en un XPath inválido para activar el self-healing
driver.type(xpath="//input[@id='sear']", text='One piece')

# Intentar presionar una tecla en un XPath inválido para activar el self-healing
driver.press(xpath="//input[@id='searnoesta']", key='Enter')

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

# Uso directo de LangChainManager para sugerir un selector alternativo
manager = LangChainManager()
suggested = manager.suggest_alternative_selector(
    "<input id='searchInput' />",
    "//input[@id='sear']",
    "type",
)
print(suggested)
