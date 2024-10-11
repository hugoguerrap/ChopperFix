
### 🫎🔬 **Chopperfix**

**Chopperfix** is a powerful library designed to automate and optimize web browser interactions. This tool integrates with **Selenium** and **Playwright**, leveraging artificial intelligence and language models to analyze, log, and continuously improve the actions performed in web environments, enabling robust automation and self-healing capabilities.

#### 🚀 **Key Features**

- **🎯 Action Decorators:** Automate and log actions with detailed descriptions and context using the `@chopperdoc` decorator, providing clear insights into each interaction.

- **🗃️ Robust Pattern Storage:** A solid system for storing patterns, tracking their usage, and evaluating their effectiveness, allowing continuous improvement of selectors and action execution.

- **🤖 AI Integration:** Uses **LangChain** and language models (e.g., GPT) to dynamically enhance selectors and interactions based on changes in the DOM of the web pages.

- **🌐 Wide Compatibility:** Works seamlessly with both **Selenium** and **Playwright**, maximizing automation capabilities and ensuring smooth integration with various browsers and web environments.

#### 🔧 **API Key and OpenAI Configuration**

To use ChopperFix with OpenAI models, you need to configure an API Key:

1. **Obtain an OpenAI API Key:**
   - Visit OpenAI’s website and create an account.
   - Generate an API Key from the dashboard.

2. **Set the API Key as an Environment Variable:**
   - In your command line or terminal, set the following environment variable:
     ```
     export OPENAI_API_KEY='your_openai_api_key_here'
     ```

#### 📚 **Installation**

To install **ChopperFix**, use the following command:
```bash
pip install chopperfix
```
Ensure that all dependencies such as **LangChain**, **Selenium**, **Playwright**, **SQLAlchemy**, and **spaCy** are properly configured in your environment.

#### 🛠️ **Integration with Playwright**

1. **Setting up Playwright**
   - Install Playwright:
     ```bash
     pip install playwright
     playwright install
     ```

2. **Implementation with ChopperFix**
   - Example of using ChopperFix with Playwright:
   ```python
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
                   break  # Exits loop if action is successfully performed
               except Exception as e:
                   print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
   ```

#### 🖥️ **Integration with Selenium**

1. **Setting up Selenium**
   - Install Selenium:
     ```bash
     pip install selenium
     ```
   - Download the appropriate WebDriver for your browser (e.g., ChromeDriver for Chrome).

2. **Implementation with ChopperFix**
   - Example of using ChopperFix with Selenium:
   ```python
   from selenium import webdriver
   from chopperfix.chopper_decorators import chopperdoc

   class CustomSelenium:
       def __init__(self, driver_path='path/to/chromedriver'):
           self.driver = webdriver.Chrome(executable_path=driver_path)

       @chopperdoc
       def perform_action(self, action, **kwargs):
           try:
               element = self.driver.find_element_by_css_selector(kwargs['selector'])
               if action == 'click':
                   element.click()
               elif action == 'type':
                   element.clear()
                   element.send_keys(kwargs.get('text', ''))
               elif action == 'navigate':
                   self.driver.get(kwargs.get('url', ''))
           except Exception as e:
               print(f"[ERROR] Action '{action}' execution failed: {e}")
   ```

#### 📊 **Pattern Storage and Analysis**

Each recorded interaction is stored in the database using the **Pattern model**, tracking statistics such as usage count, success rate, and the weight of each pattern. This allows optimization of future automation actions, improving selector robustness and self-healing performance.

### 💡 **Ideas and Future Enhancements**

- **✨ Support for more browsers:** We plan to expand compatibility to other browsers for wider coverage.
- **🔧 Continuous improvement of patterns:** Ongoing optimization of selectors and action patterns using advanced AI techniques.
- **📈 Advanced analysis and visualization:** More tools for analyzing patterns and actions will be added, providing optimization insights driven by data.

### 📝 **Contribution**

If you'd like to contribute to **ChopperFix**:

1. **Fork the project.**
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request for review.

---

### Suggestions to Enhance Self-Healing

1. **Expanding Support for Element Identifiers:**
   - **Dynamic XPath Generation:** Implement a dynamic XPath generator that adapts to small changes in the DOM structure, improving the resiliency of element identification.
   - **Fallback Identifiers:** Add backup identifiers for each element (e.g., using `data-*` attributes if available) that can be used if the primary selector fails.

2. **Improved Context Detection:**
   - **Text-Based Detection:** If the selector fails, perform a search based on the visible text of the element to re-identify it.
   - **Visual Analysis with OpenCV:** Utilize visual analysis techniques (e.g., OpenCV) to locate elements on the page even if their position or appearance has changed.

3. **Proactive Feedback and Continuous Learning:**
   - **Store and Reevaluate Failures:** Create a feedback system that adjusts selector patterns based on each failure, improving future identification.
   - **Detailed Failure Reports:** Generate detailed logs and suggestions on how to resolve issues encountered during automation, such as alternatives to selectors.

4. **Selector Heuristics and Machine Learning:**
   - **Heuristic Selector Ranking:** Use historical data to rank the robustness of various selector strategies (CSS, XPath, ID, etc.) and prioritize those that have shown higher reliability.
   - **Learning-based Recovery:** Train a model to predict the likelihood of a selector’s success based on past data, automatically switching to alternative strategies when necessary.
