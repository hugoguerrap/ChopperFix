from setuptools import setup, find_packages

setup(
    name='ChopperFix',
    version='0.0.1',
    author='Hugo Guerra',
    author_email='',
    description='Chopperfix is a powerful library designed for automation and optimization of web browser interactions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hugoguerrap/ChopperFix.git',  # Cambia a la URL de tu repositorio
    packages=find_packages(exclude=['tests*', 'examples*']),
    install_requires=[
        'sqlalchemy',
        'beautifulsoup4',
        'adalflow',
        'openai',
        'Pillow',
        'requests',
        'pydantic',
        'loguru',
        'numpy',
        'scikit-learn',
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
