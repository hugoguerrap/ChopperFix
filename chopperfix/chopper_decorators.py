from functools import wraps
from learning.pattern_storage import PatternStorage
from llm_integration.langchain_manager import LangChainManager

# Integración con LangChainManager y el decorador de acción
langchain_manager = LangChainManager()
pattern_storage = PatternStorage()


def chopperdoc(func):
    @wraps(func)
    def wrapper(driver, *args, **kwargs):
        action_name = args[0] if args else kwargs.get('action', func.__name__)
        url = driver.page.url
        selector = kwargs.get('selector')

        if action_name == 'navigate':
            selector = 'URL'
            url = kwargs.get('url', '')

        html_content = driver.page.content()

        try:
            print(f"[INFO] Ejecutando acción: {action_name} con argumentos {args} {kwargs}")
            result = func(driver, *args, **kwargs)
            print(f"[SUCCESS] Acción '{action_name}' completada con éxito.")

            description = langchain_manager.generate_description(action_name, selector, url, html_content)
            pattern_storage.save_pattern(action_name, selector, url, description, success=True)
            return result

        except Exception as e:
            print(f"[ERROR] Error al ejecutar la acción '{action_name}': {e}")
            if selector and selector != 'URL':
                print(f"[INFO] Iniciando self-healing para el selector fallido: '{selector}'")
                replacement_selector = pattern_storage.get_replacement_selector(selector, url)

                if not replacement_selector:
                    print("[INFO] Solicitando selector alternativo al LLM")
                    replacement_selector = langchain_manager.suggest_alternative_selector(html_content, selector)

                if replacement_selector:
                    print(f"[INFO] Reintentando acción con selector alternativo '{replacement_selector}'")
                    kwargs['selector'] = replacement_selector
                    try:
                        result = func(driver, action_name, **kwargs)
                        successful_description = langchain_manager.generate_description(action_name,
                                                                                        replacement_selector, url,
                                                                                        html_content)
                        pattern_storage.save_pattern(action_name, selector, url, successful_description, success=False,
                                                     replacement_selector=replacement_selector)
                        pattern_storage.save_pattern(action_name, replacement_selector, url, successful_description,
                                                     success=True)
                        return result
                    except Exception as retry_exception:
                        print(
                            f"[ERROR] Error al reintentar la acción con el selector alternativo '{replacement_selector}': {retry_exception}")
                        pattern_storage.save_pattern(action_name, replacement_selector, url, str(retry_exception),
                                                     success=False)
                else:
                    print(f"[WARN] No se pudo encontrar un selector alternativo para '{selector}'")

            pattern_storage.save_pattern(action_name, selector, url, str(e), success=False)
            raise e

    return wrapper
