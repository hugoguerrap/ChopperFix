import os
import re

from bs4 import BeautifulSoup
from adalflow.core import Generator
from adalflow.components.model_client import OpenAIClient
from adalflow.core.types import GeneratorOutput

import re

import re

import re


def fix_xpath(xpath):
    """
    Corrige el XPath para asegurar que los valores de atributos estén rodeados por comillas dobles.

    Args:
        xpath (str): El XPath generado.

    Returns:
        str: El XPath corregido.
    """
    # Expresión regular para asegurar comillas dobles alrededor del valor del atributo
    pattern = r"(@[\w-]+)=['\"]?([^'\"]+)['\"]?"
    corrected_xpath = re.sub(pattern, r'\1="\2"', xpath)

    # Corregir comillas desbalanceadas (por si acaso)
    if corrected_xpath.count('"') % 2 != 0:
        corrected_xpath = corrected_xpath.replace('="', '="').replace(']"', ']')

    return corrected_xpath

def clean_xpath(raw_response):
    """
    Limpia la respuesta del generador para extraer únicamente el XPath.

    Args:
        raw_response (str): La respuesta cruda del generador.

    Returns:
        str: El XPath limpio.
    """
    # Eliminar envolturas como ```xpath y ```
    cleaned_xpath = raw_response.strip().replace("```xpath", "").replace("```", "").strip()
    return cleaned_xpath


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
        """
        Sugiere un selector XPath alternativo utilizando el contexto HTML.
        """
        # Construye el prompt utilizando toda la información relevante
        prompt_template = (
            "Generate a robust and valid XPath selector based on the following context and HTML. Ensure all attribute values are enclosed in single quotes (`'`).\n\n"
            "- Action to perform: {action_name}\n"
            "- Failed selector: {failed_selector}\n"
            "- Full element HTML: {full_element_html}\n"
            "- Parent element HTML: {parent_element}\n"
            "- Child elements HTML: {child_elements}\n"
            "- Sibling elements HTML: {sibling_elements}\n"
            "- Current HTML:\n"
            "```html\n{html_content}\n```\n\n"
            "### XPath Guidelines:\n"
            "1. All attribute values must be enclosed in single quotes (`'`). For example:\n"
            "   - Correct: `//input[@id='searchInput']`\n"
            "   - Incorrect: `//input[@id=searchInput]`\n"
            "2. Prefer unique attributes like `id`, `name`, or `data-*` if available.\n"
            "3. If no unique attribute is available, combine attributes for robustness.\n"
            "   - Example: `//div[@class='main' and @role='button']`\n"
            "4. Use functions like `contains()` or `starts-with()` when attribute values are partial or variable.\n"
            "   - Example: `//button[contains(@class, 'submit')]`\n"
            "   - Example: `//div[starts-with(@id, 'main-section')]`\n"
            "5. Consider including `text()` in the selector if the element's content is relevant.\n"
            "   - Example: `//a[contains(text(), 'Learn More')]`\n"
            "6. Use position-based indexing (`[1]`, `[last()]`) only as a last resort.\n"
            "7. Ensure the XPath is robust enough to identify the element consistently, even if minor changes occur in the HTML.\n\n"
            "### Output Format:\n"
            "Return only the XPath selector in the following format. Ensure the syntax is valid and includes proper quotes:\n"
            "```\n"
            "//your/xpath[@attribute='value']\n"
            "```\n\n"
            "Return strictly the XPath selector. Do not include any additional text or explanations."
        )

        # Llenar el prompt con valores reales
        prompt_kwargs = {
            "action_name": action_name,
            "failed_selector": failed_selector,
            "html_content": html_content,
            "full_element_html": full_element_html or "Not available",
            "parent_element": parent_element or "Not available",
            "child_elements": ", ".join(child_elements) if child_elements else "Not available",
            "sibling_elements": ", ".join(sibling_elements) if sibling_elements else "Not available",
        }

        # Formatear el prompt
        formatted_prompt = prompt_template.format(**prompt_kwargs)

        try:
            # Llamar al generador con el prompt formateado
            response: GeneratorOutput = self.generator(prompt_kwargs={"input_str": formatted_prompt})

            if response and response.data:
                # Limpiar y corregir el XPath
                selector = response.data.strip()

                # Validar que sea un XPath válido y corregir si es necesario
                corrected_selector = clean_xpath(selector)
                corrected_selector=fix_xpath(corrected_selector)
                print("[INFO] Selector alternativo sugerido:", corrected_selector)
                return corrected_selector

            elif response and response.error:
                print("[ERROR] Error en la generación del selector:", response.error)
            else:
                print("[ERROR] No se obtuvo una respuesta válida del generador.")
        except Exception as e:
            print(f"[ERROR] Error al llamar al generador: {e}")
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

    def analyze_context_from_text(self, db_text_data, failed_selector, action_name):
        """
        Analiza el contexto textual proporcionado (todos los elementos de la base de datos en un texto)
        para identificar un selector adecuado basado en el contexto y métricas.

        Args:
            db_text_data (str): Texto que contiene todos los elementos de la base de datos.
            failed_selector (str): Selector que falló en la acción.
            action_name (str): Nombre de la acción asociada.

        Returns:
            str: Selector alternativo recomendado o None si no se encuentra uno.
        """
        # Crear el prompt para el modelo LLM
        prompt_template = (
            "The following is a dataset containing CSS selectors, their context, and metrics from a database:\n"
            "```\n{db_text_data}\n```\n\n"
            "Given this dataset, analyze the context to suggest the most suitable replacement selector "
            "for the failed selector '{failed_selector}' in the context of the action '{action_name}'.\n\n"
            "### Guidelines:\n"
            "1. Prioritize selectors with unique and stable attributes like 'id', 'name', or 'data-*'.\n"
            "2. Use context and metrics (e.g., weight, success rate) to rank potential selectors.\n"
            "3. Avoid fragile selectors based solely on class names or positions.\n"
            "4. If no suitable selector is found, return 'None'.\n\n"
            "Return only the suggested CSS selector in the following format:\n"
            "```\nCSS_SELECTOR\n```"
        )

        # Formatear el prompt con los datos proporcionados
        formatted_prompt = prompt_template.format(
            db_text_data=db_text_data,
            failed_selector=failed_selector,
            action_name=action_name
        )

        try:
            # Llamar al modelo LLM con el prompt
            response: GeneratorOutput = self.generator(prompt_kwargs={"input_str": formatted_prompt})

            if response and response.data:
                # Procesar la respuesta del modelo
                selector = response.data.strip()
                selector = re.sub(r'[`\'"\n]', '', selector)  # Limpiar comillas y saltos de línea
                if selector.lower() == "none":
                    print("[WARN] El modelo no pudo sugerir un selector válido.")
                    return None
                print(f"[INFO] Selector sugerido por LLM: {selector}")
                return selector

            print("[ERROR] No se obtuvo una respuesta válida del generador LLM.")
            return None

        except Exception as e:
            print(f"[ERROR] Error al analizar el contexto desde el texto: {e}")
            return None


