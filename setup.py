from setuptools import setup, find_packages

setup(
    name='ChopperFix',
    version='0.1.0',
    author='Hugo Guerra',
    author_email='',
    description='Librería de self-healing para automatización web con análisis y reconocimiento de patrones',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hugoguerrap/ChopperFix.git',  # Cambia a la URL de tu repositorio
    packages=find_packages(exclude=['tests*', 'examples*']),
    install_requires=[
        'sqlalchemy',
        'playwright',
        'beautifulsoup4',
        'langchain-openai',
        # Agrega más dependencias según sea necesario
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md'],
    },
)
