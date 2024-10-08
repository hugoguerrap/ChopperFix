import re
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import wraps
from llm_integration.langchain_manager import LangChainManager

# Crear la base de datos SQLAlchemy
Base = declarative_base()

class Pattern(Base):
    __tablename__ = 'patterns'

    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    selector = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    peso = Column(Float, default=1.0)  # Campo de peso para priorizar patrones

    def __repr__(self):
        return f"<Pattern(action={self.action}, selector={self.selector}, peso={self.peso}, url={self.url})>"

class PatternStorage:
    def __init__(self, db_url='sqlite:///patterns.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def normalize_selector(self, selector):
        """
        Normaliza el selector eliminando espacios adicionales, convirtiéndolo a minúsculas
        y eliminando cualquier símbolo innecesario.
        """
        normalized = re.sub(r'\s+', '', selector.lower())  # Eliminar espacios y convertir a minúsculas
        return normalized

    def save_pattern(self, action, selector, url, description):
        # Normalizar el selector antes de guardarlo
        normalized_selector = self.normalize_selector(selector)

        # Verificar si el patrón ya existe en la base de datos
        existing_pattern = self.session.query(Pattern).filter_by(
            action=action,
            selector=normalized_selector,
            url=url
        ).first()

        if existing_pattern:
            # Incrementar el peso del patrón ya existente si se utilizó exitosamente
            existing_pattern.peso += 1.0
            existing_pattern.description = description  # Actualizar la descripción
            existing_pattern.timestamp = datetime.utcnow()
            print(f"Patrón actualizado con peso incrementado: {existing_pattern.selector} para la URL {url}")
        else:
            # Si no existe, lo agregamos a la base de datos como un nuevo patrón con peso inicial
            new_pattern = Pattern(action=action, selector=normalized_selector, url=url, description=description, peso=1.0)
            self.session.add(new_pattern)
            print(f"Nuevo patrón guardado: {normalized_selector} para la URL {url}")

        # Guardamos los cambios en la base de datos
        self.session.commit()

    def get_similar_selector(self, failed_selector, url):
        # Normalizar el selector antes de buscarlo
        normalized_failed_selector = self.normalize_selector(failed_selector)

        # Buscar patrones similares en la base de datos, ordenados por peso descendente
        similar_patterns = self.session.query(Pattern).filter(
            Pattern.url == url,
            Pattern.selector.like(f"%{normalized_failed_selector}%")
        ).order_by(Pattern.peso.desc()).all()

        if similar_patterns:
            # Devolver el selector con mayor peso encontrado
            print(f"Patrón encontrado en base de datos con mayor peso: {similar_patterns[0].selector}, peso: {similar_patterns[0].peso}")
            return similar_patterns[0].selector
        else:
            return None

    def get_patterns(self, limit=10):
        """Obtiene los patrones más recientes, limitados por la cantidad especificada."""
        patterns = self.session.query(Pattern).order_by(Pattern.timestamp.desc()).limit(limit).all()
        return patterns

    def close(self):
        self.engine.dispose()


