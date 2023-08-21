# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os, sys
sys.path.insert(0, os.path.abspath("../"))

project = 'pyDXHR'
copyright = '2023'
author = 'Vardonir'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    "myst_parser",
    "nbsphinx",
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_show_sourcelink = False
html_show_sphinx = False

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
html_css_files = ["colors.css"]

html_logo = '_static/pydxhr_logo.png'
html_theme_options = {
    'analytics_id': 'G-3VLGR2WY44',
    'prev_next_buttons_location': None,
    'logo_only': True,
    'display_version': False,
}

# command for terminal: sphinx-build -b html sphinx_docs/ docs -E