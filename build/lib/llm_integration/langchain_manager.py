from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

from utils.config import Config

class LangChainManager:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-4o-mini',api_key=Config.OPENAI_API_KEY)

    def suggest_alternative_selector(self, html_content, failed_selector):
        # Definir una plantilla de prompt específica para obtener un selector CSS corto y aplicable
        prompt_template = PromptTemplate(
            input_variables=["html", "selector"],
            template=(
                "Given the following HTML structure:\n\n```html\n{html}\n```\n\n"
                "The current selector '{selector}' failed to locate an element. "
                "Please provide a valid CSS selector that can be used as an alternative.\n\n"
                "### Examples of valid CSS selectors:\n"
                "- For an element with the class 'button-primary': `.button-primary`\n"
                "- For the first paragraph inside a div: `div p:first-of-type`\n"
                "- For an element with the ID 'submit-btn': `#submit-btn`\n"
                "- To target all anchor tags: `a`\n\n"
                "### Output:\n"
                "Return only a valid CSS selector in this format:\n"
                "```\nCSS_SELECTOR\n```"
            )
        )

        # Crear una cadena de ejecución utilizando RunnableSequence
        chain = prompt_template | self.llm
        response = chain.invoke({"html": html_content, "selector": failed_selector})

        # Extraer el selector directamente del bloque de código Markdown
        if response:
            selector = response.content.strip().replace('```', '').strip()
            return selector
        return None

    def generate_description(self, action_name, selector, url, html_content):
        # Extraer un subconjunto extenso del HTML usando BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Lista completa de elementos importantes para la curación y contexto del self-healing
        important_elements = soup.find_all([
            'input', 'button', 'a', 'select', 'textarea', 'form',  # Elementos interactivos
            'div', 'span', 'section', 'article', 'header', 'footer',  # Elementos estructurales
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'ul', 'ol',  # Elementos de texto
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',  # Elementos de tabla
            'img', 'svg', 'video', 'audio', 'canvas'  # Elementos multimedia
        ])

        # Limitar a los primeros 50 elementos para mantener el contexto manejable
        truncated_html = '\n'.join(str(element) for element in important_elements[:50])

        prompt = f"""
        Given the following details of a web automation action:
        - Action: {action_name}
        - Selector: {selector}
        - URL: {url}
        - HTML Content (truncated): 
        ```
        {truncated_html}
        ```

        Please generate a concise description of this action in the context of the web page's structure.
        """
        response = self.llm.invoke(prompt)
        return response.content.strip()