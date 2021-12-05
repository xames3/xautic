# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys

import guzzle_sphinx_theme

sys.path.insert(0, os.path.abspath("../xautic/"))

from xautic import __version__

# -- Project information -----------------------------------------------------
project = "xautic"
copyright = "2021, Akshay Mestry (XAMES3)"
author = "Akshay Mestry (XAMES3)"

# The full version, including alpha/beta/rc tags
release = __version__

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "guzzle_sphinx_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_translator_class = "guzzle_sphinx_theme.HTMLTranslator"
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = "guzzle_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Custom sidebar templates, maps document names to template names.
html_show_sourcelink = False
html_show_sphinx = False
html_sidebars = {"**": ["logo-text.html", "globaltoc.html", "searchbox.html"]}

html_theme_options = {
    "homepage": "index",
    "projectlink": "http://github.com/xames3/xautic/",
    "project_nav_name": f"xautic v{__version__} documentation",
}

autoclass_content = "both"
