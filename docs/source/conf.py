import os
import sys

# Insert project root to sys.path so autodoc can import project modules
sys.path.insert(0, os.path.abspath('../../'))

project = 'FILMATE Backend'
author = 'Equipo FILMATE'
language = 'es'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.openapi',
]

# Mock heavy or environment-dependent imports so autodoc can import modules safely
autodoc_mock_imports = [
    'sqlalchemy',
    'pydantic',
    'fastapi',
    'dotenv',
    'pymysql',
    'app.core.database',
]

autosummary_generate = True
autoclass_content = 'both'

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_title = 'Documentación de FILMATE Backend'
html_static_path = ['_static']

# Autodoc default options
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
