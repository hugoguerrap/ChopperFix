from functools import wraps  # Importa el decorador 'wraps' para mantener la metadata de la función original
from learning.pattern_storage import PatternStorage  # Importa la clase 'PatternStorage' para almacenar patrones
from llm_integration.adalflow_manager import AdalFlowManager
from bs4 import BeautifulSoup  # Necesario para extraer el contexto del HTML

# Inicializa las instancias de AdalFlowManager y PatternStorage
pattern_storage = PatternStorage()
adalFlow_Manger = AdalFlowManager()

def extract_element_context(html_content, selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_element = soup.select_one(selector)

    if not target_element:
        return None, None, None, None

    parent_element = target_element.parent
    child_elements = [str(child) for child in target_element.children if child.name]
    sibling_elements = [str(sibling) for sibling in target_element.find_next_siblings()]

    return str(target_element), str(parent_element), child_elements, sibling_elements

def chopperdoc(func):  # Define un decorador llamado 'chopperdoc' que toma una función como argumento
    @wraps(func)  # Mantiene la metadata de la función original
    def wrapper(driver, *args, **kwargs):  # Define la función envoltura que recibe un controlador y argumentos
        action_name = args[0] if args else kwargs.get('action', func.__name__)  # Obtiene el nombre de la acción
        url = driver.page.url  # Obtiene la URL actual de la página
        selector = kwargs.get('selector')  # Obtiene el selector de los argumentos

        if action_name == 'navigate':  # Si la acción es 'navigate'
            selector = 'URL'  # Establece el selector como 'URL'
            url = kwargs.get('url', '')  # Obtiene la URL de los argumentos

        html_content = driver.page.content()  # Obtiene el contenido HTML de la página

        # Extraer el contexto del elemento HTML antes de ejecutar la acción
        full_element_html, parent_element, child_elements, sibling_elements = extract_element_context(html_content, selector)

        try:
            print(f"[INFO] Ejecutando acción: {action_name} con argumentos {args} {kwargs}")  # Imprime información sobre la acción
            result = func(driver, *args, **kwargs)  # Llama a la función original con los argumentos
            print(f"[SUCCESS] Acción '{action_name}' completada con éxito.")  # Imprime mensaje de éxito

            # Llamar a generate_description con el contexto completo
            description = adalFlow_Manger.generate_description(
                action_name, selector, url, html_content,
                full_element_html=full_element_html,
                parent_element=parent_element,
                child_elements=child_elements,
                sibling_elements=sibling_elements
            )  # Genera una descripción de la acción

            # Guardar el patrón exitoso junto con el contexto HTML
            pattern_storage.save_pattern(
                action_name, selector, url, description, success=True,
                full_element_html=full_element_html,
                parent_element=parent_element,
                child_elements=child_elements,
                sibling_elements=sibling_elements
            )
            return result  # Devuelve el resultado de la función original

        except Exception as e:  # Captura cualquier excepción que ocurra
            print(f"[ERROR] Error al ejecutar la acción '{action_name}': {e}")  # Imprime el error
            if selector and selector != 'URL':  # Si hay un selector y no es 'URL'
                print(f"[INFO] Iniciando self-healing para el selector fallido: '{selector}'")  # Inicia el proceso de auto-reparación

                replacement_selector = pattern_storage.get_replacement_selector(selector, url)  # Intenta obtener un selector alternativo

                if not replacement_selector:  # Si no se encontró un selector alternativo
                    print("[INFO] Solicitando selector alternativo al LLM")  # Solicita un selector alternativo al LLM

                    # Llamar a suggest_alternative_selector con el contexto completo
                    replacement_selector = adalFlow_Manger.suggest_alternative_selector(
                        html_content, selector, action_name,
                        full_element_html=full_element_html,
                        parent_element=parent_element,
                        child_elements=child_elements,
                        sibling_elements=sibling_elements
                    )  # Sugiere un selector alternativo

                if replacement_selector:  # Si se encontró un selector alternativo
                    print(f"[INFO] Reintentando acción con selector alternativo '{replacement_selector}'")  # Imprime información sobre el reintento
                    kwargs['selector'] = replacement_selector  # Actualiza el selector en los argumentos
                    try:
                        result = func(driver, action_name, **kwargs)  # Reintenta la acción con el nuevo selector
                        # Llamar a generate_description con el contexto completo para el intento exitoso
                        successful_description = adalFlow_Manger.generate_description(
                            action_name, replacement_selector, url, html_content,
                            full_element_html=full_element_html,
                            parent_element=parent_element,
                            child_elements=child_elements,
                            sibling_elements=sibling_elements
                        )  # Genera descripción del intento exitoso
                        pattern_storage.save_pattern(action_name, selector, url, successful_description, success=False, replacement_selector=replacement_selector)  # Guarda el patrón del intento fallido
                        pattern_storage.save_pattern(action_name, replacement_selector, url, successful_description, success=True)  # Guarda el patrón exitoso con el nuevo selector
                        return result  # Devuelve el resultado del reintento
                    except Exception as retry_exception:  # Captura cualquier excepción en el reintento
                        print(f"[ERROR] Error al reintentar la acción con el selector alternativo '{replacement_selector}': {retry_exception}")  # Imprime el error del reintento
                        pattern_storage.save_pattern(action_name, replacement_selector, url, str(retry_exception), success=False)  # Guarda el patrón del reintento fallido
                else:  # Si no se pudo encontrar un selector alternativo
                    print(f"[WARN] No se pudo encontrar un selector alternativo para '{selector}'")  # Imprime advertencia

                # Guardar el patrón fallido con el contexto del elemento HTML
                pattern_storage.save_pattern(
                    action_name, selector, url, str(e), success=False,
                    full_element_html=full_element_html,
                    parent_element=parent_element,
                    child_elements=child_elements,
                    sibling_elements=sibling_elements
                )

            raise e  # Vuelve a lanzar la excepción

    return wrapper  # Devuelve la función envoltura
