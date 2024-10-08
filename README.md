
# 🫎🔬 Chopperfix

Chopperfix is a powerful library designed for automation and optimization of web browser interactions. This tool integrates with Selenium and Playwright, using artificial intelligence and language models to analyze, log, and continuously improve the actions performed in web environments.

## 🚀 Key Features

- **🎯 Action Decorators**: Automate and log actions with detailed descriptions.
- **🗃️ Pattern Storage**: Robust system for storing patterns, tracking their usage, and assessing their effectiveness.
- **🤖 AI Integration**: Uses LangChain to continuously enhance selectors and interactions with language models.
- **🌐 Compatibility**: Works seamlessly with both Selenium and Playwright to maximize automation capabilities.

## 📚 Installation

To get started, make sure you have Python installed on your system. Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

> Ensure that `LangChain`, `Selenium`, `Playwright`, `SQLAlchemy`, and `spacy` are properly configured in your environment.

## 🛠️ Integration with Playwright

### 1. Setting up Playwright

First, make sure Playwright is installed:
```bash
pip install playwright
playwright install
```

### 2. Implementation with `chopperfix`

Here is an example of how to use `chopperfix` with Playwright, following the logic demonstrated before:

```python
from playwright.sync_api import sync_playwright
from core.action_decorators import action_logger

class CustomPlaywright:
    def __init__(self, timeout=10000, retry_attempts=1):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(timeout)
        self.retry_attempts = retry_attempts

    @action_logger
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
                break  # Exits loop if action is successfully performed
            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
```

### 3. How it works

- Uses the `@action_logger` decorator to log each action performed with Playwright.
- Actions like `click`, `type`, `press`, and `navigate` are automatically logged with detailed descriptions generated by LangChain.

## 🖥️ Integration with Selenium

### 1. Setting up Selenium

First, ensure that Selenium is installed:
```bash
pip install selenium
```

Download the appropriate WebDriver for your browser (e.g., [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) if using Chrome).

### 2. Implementation with `chopperfix`

Here is a similar example to the one with Playwright but using Selenium:

```python
from selenium import webdriver
from core.action_decorators import action_logger

class CustomSelenium:
    def __init__(self, driver_path='path/to/chromedriver'):
        self.driver = webdriver.Chrome(executable_path=driver_path)

    @action_logger
    def perform_action(self, action, **kwargs):
        try:
            if action == 'click':
                self.driver.find_element_by_css_selector(kwargs['selector']).click()
            elif action == 'type':
                element = self.driver.find_element_by_css_selector(kwargs['selector'])
                element.clear()
                element.send_keys(kwargs.get('text', ''))
            elif action == 'navigate':
                self.driver.get(kwargs.get('url', ''))
        except Exception as e:
            print(f"[ERROR] Action '{action}' execution failed: {e}")
```

### 3. How it works

- Actions are decorated with `@action_logger`, allowing you to capture detailed information about each interaction.
- LangChain generates comprehensive descriptions of each action and suggests improvements in case of failures.

## 📊 Pattern Storage and Analysis

Each recorded interaction is stored in the database using the `Pattern` model. It tracks statistics like usage count, success rate, and weight of each pattern, allowing optimization of future actions.

## 📄 Contribution

If you would like to contribute to `chopperfix`, please follow these steps:
1. Fork the project.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

## 💡 Ideas and Future Enhancements

- **✨ Integration with other browsers**.
- **🔧 Continuous improvement of selectors and action patterns using AI**.
- **📈 Advanced analysis and visualization of action and pattern statistics**.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

