import re
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


def fix_xpath(xpath: str) -> str:
    pattern = r"(@[\w-]+)=['\"]?([^'\"]+)['\"]?"
    corrected_xpath = re.sub(pattern, r'\1="\2"', xpath)
    if corrected_xpath.count('"') % 2 != 0:
        corrected_xpath = corrected_xpath.replace('="', '="').replace(']"', ']')
    return corrected_xpath


def clean_xpath(raw_response: str) -> str:
    cleaned_xpath = raw_response.strip().replace("```xpath", "").replace("```", "").strip()
    return cleaned_xpath


class LangChainManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo-0125", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def suggest_alternative_selector(
        self,
        html_content: str,
        failed_selector: str,
        action_name: str,
        full_element_html: str | None = None,
        parent_element: str | None = None,
        child_elements: list[str] | None = None,
        sibling_elements: list[str] | None = None,
    ) -> str | None:
        template = (
            "Generate a robust and valid XPath selector based on the following context and HTML."
            " Ensure all attribute values are enclosed in single quotes (`'`).\n\n"
            "- Action to perform: {action_name}\n"
            "- Failed selector: {failed_selector}\n"
            "- Full element HTML: {full_element_html}\n"
            "- Parent element HTML: {parent_element}\n"
            "- Child elements HTML: {child_elements}\n"
            "- Sibling elements HTML: {sibling_elements}\n"
            "- Current HTML:\n```html\n{html_content}\n```\n\n"
            "Return only the XPath selector."
        )
        prompt = PromptTemplate(
            input_variables=[
                "action_name",
                "failed_selector",
                "full_element_html",
                "parent_element",
                "child_elements",
                "sibling_elements",
                "html_content",
            ],
            template=template,
        )
        formatted = prompt.format(
            action_name=action_name,
            failed_selector=failed_selector,
            full_element_html=full_element_html or "Not available",
            parent_element=parent_element or "Not available",
            child_elements=", ".join(child_elements) if child_elements else "Not available",
            sibling_elements=", ".join(sibling_elements) if sibling_elements else "Not available",
            html_content=html_content,
        )
        try:
            response = self.llm.predict(formatted)
            selector = fix_xpath(clean_xpath(response))
            return selector if selector else None
        except Exception as e:
            print(f"[ERROR] LangChain suggestion failed: {e}")
            return None

    def generate_description(
        self,
        action_name: str,
        selector: str,
        url: str,
        html_content: str,
        full_element_html: str | None = None,
        parent_element: str | None = None,
        child_elements: list[str] | None = None,
        sibling_elements: list[str] | None = None,
    ) -> str | None:
        soup = BeautifulSoup(html_content, "html.parser")
        important = soup.find_all([
            "input",
            "button",
            "a",
            "select",
            "textarea",
            "form",
            "div",
            "span",
            "section",
            "article",
            "header",
            "footer",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "li",
            "ul",
            "ol",
            "table",
            "tr",
            "td",
            "th",
            "thead",
            "tbody",
            "tfoot",
            "img",
            "svg",
            "video",
            "audio",
            "canvas",
        ])
        truncated_html = "\n".join(str(el) for el in important[:50])
        template = (
            "Given the following details of a web automation action:\n"
            "- Action: {action_name}\n"
            "- Selector: {selector}\n"
            "- URL: {url}\n"
            "- Full element HTML: {full_element_html}\n"
            "- Parent element HTML: {parent_element}\n"
            "- Child elements HTML: {child_elements}\n"
            "- Sibling elements HTML: {sibling_elements}\n"
            "- HTML Content (truncated):\n```\n{truncated_html}\n```\n\n"
            "Please generate a concise description of this action in the context of the web page's structure."
        )
        prompt = PromptTemplate(
            input_variables=[
                "action_name",
                "selector",
                "url",
                "full_element_html",
                "parent_element",
                "child_elements",
                "sibling_elements",
                "truncated_html",
            ],
            template=template,
        )
        formatted = prompt.format(
            action_name=action_name,
            selector=selector,
            url=url,
            full_element_html=full_element_html or "Not available",
            parent_element=parent_element or "Not available",
            child_elements=", ".join(child_elements) if child_elements else "Not available",
            sibling_elements=", ".join(sibling_elements) if sibling_elements else "Not available",
            truncated_html=truncated_html,
        )
        try:
            description = self.llm.predict(formatted)
            return description.strip()
        except Exception as e:
            print(f"[ERROR] LangChain description failed: {e}")
            return None

    def analyze_context_from_text(
        self,
        db_text_data: str,
        failed_selector: str,
        action_name: str,
    ) -> str | None:
        template = (
            "The following is a dataset containing CSS selectors, their context, and metrics from a database:\n"
            "```\n{db_text_data}\n```\n\n"
            "Given this dataset, analyze the context to suggest the most suitable replacement selector "
            "for the failed selector '{failed_selector}' in the context of the action '{action_name}'.\n\n"
            "Return only the suggested CSS selector."
        )
        prompt = PromptTemplate(
            input_variables=["db_text_data", "failed_selector", "action_name"],
            template=template,
        )
        formatted = prompt.format(
            db_text_data=db_text_data,
            failed_selector=failed_selector,
            action_name=action_name,
        )
        try:
            selector = self.llm.predict(formatted)
            selector = re.sub(r'[`\'"\n]', '', selector).strip()
            return None if selector.lower() == "none" else selector
        except Exception as e:
            print(f"[ERROR] LangChain context analysis failed: {e}")
            return None
