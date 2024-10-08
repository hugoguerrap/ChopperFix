from functools import wraps
from learning.pattern_storage import PatternStorage
from llm_integration.langchain_manager import LangChainManager

# Integración con LangChainManager y el decorador de acción
langchain_manager = LangChainManager()
pattern_storage = PatternStorage()

def action_logger(func):
    @wraps(func)
    def wrapper(driver, *args, **kwargs):
        action_name = func.__name__
        url = driver.page.url  # Captura la URL actual de la página
        selector = kwargs.get('selector', args[0] if args else None)
        html_content = driver.page.content()  # Obtener el HTML de la página

        try:
            print(f"Ejecutando acción: {action_name} con argumentos {args} {kwargs}")
            result = func(driver, *args, **kwargs)
            print(f"Acción '{action_name}' completada con éxito.")

            # Generar una descripción utilizando el LLM con el HTML incluido
            description = langchain_manager.generate_description(action_name, selector, url, html_content)

            # Guardar la acción en la base de datos de patrones con la descripción generada
            pattern_storage.save_pattern(action_name, selector, url, description)
            return result
        except Exception as e:
            print(f"Error al ejecutar la acción '{action_name}': {e}")
            if selector:
                print(f"Iniciando self-healing para el selector fallido: {selector}")

                # Consultar la base de datos de patrones para encontrar un selector alternativo
                alternative_selector = pattern_storage.get_similar_selector(selector, url)
                if alternative_selector and not alternative_selector.startswith('http'):
                    # Verifica que el selector alternativo no sea una URL
                    print(f"Selector alternativo encontrado en la base de datos: {alternative_selector}. Verificando su presencia...")
                else:
                    # Si no se encuentra en la base de datos, usar el LLM para sugerir un selector alternativo
                    alternative_selector = langchain_manager.suggest_alternative_selector(html_content, selector)
                    if alternative_selector and not alternative_selector.startswith('http'):
                        # Verifica que el selector alternativo sugerido por el LLM no sea una URL
                        print(f"Selector alternativo encontrado por el LLM: {alternative_selector}. Verificando su presencia...")

                        # Intentar guardar el nuevo patrón sugerido por el LLM si se utilizó con éxito
                        pattern_storage.save_pattern(action_name, alternative_selector, url, f"Sugerido por LLM")

                # Validar si el selector alternativo está presente antes de reintentar la acción
                if alternative_selector and not alternative_selector.startswith('http') and driver.page.query_selector(alternative_selector) is not None:
                    print(f"Selector alternativo '{alternative_selector}' está presente. Reintentando acción...")
                    kwargs['selector'] = alternative_selector
                    result = func(driver, *args, **kwargs)

                    # Si el selector alternativo funcionó, guardarlo como nuevo patrón
                    pattern_storage.save_pattern(action_name, alternative_selector, url, f"Sugerido y exitoso por LLM")

                    return result
                else:
                    print(f"No se pudo encontrar un selector alternativo adecuado o el selector alternativo era una URL.")
            raise e

    return wrapper
