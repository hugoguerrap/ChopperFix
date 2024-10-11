import re

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, JSON, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Pattern(Base):
    __tablename__ = 'patterns'

    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    selector = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    full_element_html = Column(Text)  # HTML completo del elemento
    parent_element = Column(Text)  # HTML del elemento padre
    child_elements = Column(JSON)  # HTML de los elementos hijos
    sibling_elements = Column(JSON)  # HTML de los elementos adyacentes
    peso = Column(Float, default=1.0)  # Definición del campo 'peso'
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    failed = Column(Boolean, default=False)
    replacement_selector = Column(String, nullable=True)

    def __repr__(self):
        return (f"<Pattern(action={self.action}, selector={self.selector}, "
                f"full_element_html={self.full_element_html}, parent_element={self.parent_element})>")


    def __repr__(self):
        return (f"<Pattern(action={self.action}, selector={self.selector}, "
                f"full_element_html={self.full_element_html}, parent_element={self.parent_element})>")


class PatternStorage:
    def __init__(self, db_url='sqlite:///patterns.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        #self.nlp = self.load_spacy_model()

    #def load_spacy_model(self):
    #    model_name = 'en_core_web_sm'
    #    try:
    #        return spacy.load(model_name)
    #    except OSError:
    #        print(f"Modelo {model_name} no encontrado. Descargando ahora...")
    #        subprocess.run(['python', '-m', 'spacy', 'download', model_name], check=True)
    #        return spacy.load(model_name)

    #def extract_html_context(self, html_content):
    #    doc = self.nlp(html_content)
    #    keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    #    return keywords

    def normalize_selector(self, selector):
        if not selector:
            return selector
        normalized = re.sub(r'\s+', '', selector.strip())
        normalized = re.sub(r'[\"\'<>]', '', normalized)
        return normalized

    def normalize_url(self, url):
        # Eliminar el protocolo y www si está presente
        url = re.sub(r'^(https?://)?(www\.)?', '', url)
        # Eliminar parámetros de consulta y fragmentos
        url = re.sub(r'\?.*$', '', url)
        url = re.sub(r'#.*$', '', url)
        # Eliminar barra final si está presente
        url = url.rstrip('/')
        return url

    def update_original_pattern(self, action, original_selector, url, replacement_selector):
        normalized_url = self.normalize_url(url)
        pattern = self.session.query(Pattern).filter_by(
            action=action,
            selector=self.normalize_selector(original_selector),
            url=normalized_url
        ).first()

        if pattern:
            pattern.replacement_selector = replacement_selector
            pattern.failed = True
            self.session.commit()
            print(f"Patrón original actualizado: {original_selector} -> {replacement_selector}")

    def save_pattern(self, action, selector, url, description, success=True, replacement_selector=None,
                     full_element_html=None, parent_element=None, child_elements=None, sibling_elements=None):
        normalized_selector = self.normalize_selector(selector)
        normalized_url = self.normalize_url(url)

        # Buscar el patrón existente en la base de datos
        existing_pattern = self.session.query(Pattern).filter_by(
            action=action,
            selector=normalized_selector,
            url=normalized_url
        ).first()

        if existing_pattern:
            # Actualizar el patrón existente con nuevos valores y estadísticas
            existing_pattern.usage_count += 1
            existing_pattern.success_rate = (
                    (existing_pattern.success_rate * (existing_pattern.usage_count - 1) + (1 if success else 0))
                    / existing_pattern.usage_count
            )
            existing_pattern.failed = not success
            if not success and replacement_selector:
                existing_pattern.replacement_selector = replacement_selector
            existing_pattern.description = description
            existing_pattern.timestamp = datetime.utcnow()
            existing_pattern.peso += 0.1 if success else -0.1

            # Actualizar los detalles del contexto HTML si están disponibles
            if full_element_html:
                existing_pattern.full_element_html = full_element_html
            if parent_element:
                existing_pattern.parent_element = parent_element
            if child_elements:
                existing_pattern.child_elements = child_elements
            if sibling_elements:
                existing_pattern.sibling_elements = sibling_elements

            print(f"Patrón actualizado: {existing_pattern.selector} para la URL {normalized_url}")
        else:
            # Crear un nuevo patrón si no existe uno con el mismo selector y URL
            new_pattern = Pattern(
                action=action,
                selector=normalized_selector,
                url=normalized_url,
                description=description,
                peso=1.0,
                usage_count=1,
                success_rate=1.0 if success else 0.0,
                failed=not success,
                replacement_selector=replacement_selector,
                full_element_html=full_element_html,
                parent_element=parent_element,
                child_elements=child_elements,
                sibling_elements=sibling_elements
            )
            self.session.add(new_pattern)
            print(f"Nuevo patrón guardado: {normalized_selector} para la URL {normalized_url}")

        self.session.commit()


    def get_patterns(self, failed_selector, url, limit=10):
        normalized_failed_selector = self.normalize_selector(failed_selector)
        normalized_url = self.normalize_url(url)

        # Buscar patrones exactos y similares
        patterns = self.session.query(Pattern).filter(
            and_(
                Pattern.url == normalized_url,
                Pattern.failed == False,
                or_(
                    Pattern.selector == normalized_failed_selector,
                    Pattern.selector.like(f"%{normalized_failed_selector}%"),
                    Pattern.replacement_selector == normalized_failed_selector,
                    Pattern.replacement_selector.like(f"%{normalized_failed_selector}%")
                )
            )
        ).order_by(Pattern.peso.desc(), Pattern.success_rate.desc()).limit(limit).all()

        if patterns:
            best_pattern = patterns[0]
            print(
                f"[INFO] Patrón encontrado para el selector: '{normalized_failed_selector}' con peso: {best_pattern.peso}")
            return best_pattern.selector if best_pattern.selector != normalized_failed_selector else best_pattern.replacement_selector

        print(
            f"[WARN] No se encontraron patrones para el selector: '{normalized_failed_selector}' en la URL '{normalized_url}'")
        return None

    def get_replacement_selector(self, failed_selector, url):
        normalized_failed_selector = self.normalize_selector(failed_selector)
        normalized_url = self.normalize_url(url)

        # Buscar un patrón existente con el selector fallido
        pattern = self.session.query(Pattern).filter_by(
            selector=normalized_failed_selector,
            url=normalized_url,
            failed=True
        ).order_by(Pattern.usage_count.desc()).first()

        if pattern and pattern.replacement_selector:
            print(f"[INFO] Selector de reemplazo encontrado en la base de datos: '{pattern.replacement_selector}'")
            return pattern.replacement_selector

        print(f"[WARN] No se encontró un selector de reemplazo para '{failed_selector}' en la URL '{url}'")
        return None


    def get_all_patterns(self, limit=10):
        patterns = self.session.query(Pattern).order_by(Pattern.timestamp.desc()).limit(limit).all()
        return patterns

    def close(self):
        self.session.close()
        self.engine.dispose()