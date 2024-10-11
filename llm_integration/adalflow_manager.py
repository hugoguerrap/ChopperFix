import os
import re

from bs4 import BeautifulSoup
from adalflow.core import Generator
from adalflow.components.model_client import OpenAIClient
from adalflow.core.types import GeneratorOutput

class AdalFlowManager:
    def __init__(self):
        # Inicializando el Generator con el cliente de modelo OpenAI
        openai_api_key = os.getenv('OPENAI_API_KEY')

        try:
            self.generator = Generator(
                model_client=OpenAIClient(),
                model_kwargs={"model": "gpt-4o-mini"},
            )
            print("[INFO] AdalFlow Generator inicializado correctamente.")
        except Exception as e:
            print(f"[ERROR] Error al inicializar el AdalFlow Generator: {e}")

    def suggest_alternative_selector(self, html_content, failed_selector, action_name, full_element_html=None,
                                     parent_element=None, child_elements=None, sibling_elements=None):
        # Construye el prompt usando toda la información de contexto disponible
        prompt_template = (
            "Given the following context and HTML of the page:\n"
            "- Action to perform: {action_name}\n"
            "- Failed selector: {failed_selector}\n"
            "- Full element HTML: {full_element_html}\n"
            "- Parent element HTML: {parent_element}\n"
            "- Child elements HTML: {child_elements}\n"
            "- Sibling elements HTML: {sibling_elements}\n"
            "- Current HTML:\n"
            "```html\n{html_content}\n```\n\n"
            "Please generate a robust CSS selector that is suitable for the specified action.\n\n"
            "### Guidelines for suggesting selectors:\n"
            "1. Prefer IDs over classes when available.\n"
            "2. Use specific attributes like 'name' or 'data-*' if present.\n"
            "3. Consider the role and context of the element within the page.\n"
            "4. Avoid overly complex or fragile selectors.\n\n"
            "Return only a valid CSS selector in the following format:\n"
            "```\nCSS_SELECTOR\n```"
        )

        prompt_kwargs = {
            "action_name": action_name,
            "failed_selector": failed_selector,
            "html_content": html_content,
            "full_element_html": full_element_html or "Not available",
            "parent_element": parent_element or "Not available",
            "child_elements": ", ".join(child_elements) if child_elements else "Not available",
            "sibling_elements": ", ".join(sibling_elements) if sibling_elements else "Not available"
        }

        formatted_prompt = prompt_template.format(**prompt_kwargs)

        try:
            # Llamar al Generator utilizando el prompt formateado
            response: GeneratorOutput = self.generator(prompt_kwargs={"input_str": formatted_prompt})

            if response and response.data:
                # Limpiar el selector alternativo para eliminar las comillas invertidas y espacios extra
                selector = response.data.strip()
                selector = re.sub(r'[`\'"\n]', '',
                                  selector)  # Remover comillas invertidas, dobles, simples y saltos de línea
                print("[INFO] Selector alternativo sugerido por AdalFlow:", selector)
                return selector
            elif response and response.error:
                print("[ERROR] Error en la generación del selector con AdalFlow:", response.error)
            else:
                print("[ERROR] No se obtuvo una respuesta válida del generador de AdalFlow.")
        except Exception as e:
            print(f"[ERROR] Error al llamar al generador de AdalFlow: {e}")
        return None

    def generate_description(self, action_name, selector, url, html_content, full_element_html=None,
                             parent_element=None, child_elements=None, sibling_elements=None):
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

        # Formatear el prompt para el generador de AdalFlow
        prompt_template = f"""
            Given the following details of a web automation action:
            - Action: {action_name}
            - Selector: {selector}
            - URL: {url}
            - Full element HTML: {full_element_html or "Not available"}
            - Parent element HTML: {parent_element or "Not available"}
            - Child elements HTML: {", ".join(child_elements) if child_elements else "Not available"}
            - Sibling elements HTML: {", ".join(sibling_elements) if sibling_elements else "Not available"}
            - HTML Content (truncated): 
            ```
            {truncated_html}
            ```

            Please generate a concise description of this action in the context of the web page's structure.
        """

        try:
            # Llamar al Generator utilizando el prompt formateado
            response: GeneratorOutput = self.generator(prompt_kwargs={"input_str": prompt_template})

            # Manejo del resultado y errores del GeneratorOutput
            if response and response.data:
                description = response.data.strip()
                print("[INFO] Descripción generada por AdalFlow:", description)
                return description
            elif response and response.error:
                print("[ERROR] Error en la generación de la descripción con AdalFlow:", response.error)
            else:
                print("[ERROR] No se obtuvo una respuesta válida del generador de AdalFlow.")
        except Exception as e:
            print(f"[ERROR] Error al generar la descripción con AdalFlow: {e}")
        return None


