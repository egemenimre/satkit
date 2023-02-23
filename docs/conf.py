# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys


sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "satkit"
copyright = "2023, Egemen Imre"
author = "Egemen Imre"

# Version Info
# ------------
# The short X.Y version.
version = "0.0.1"
# The full version, including alpha/beta/rc tags.
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# By default, highlight as Python 3.
highlight_language = "python3"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # "autoapi.extension",
    "sphinx.ext.autodoc",  # auto api generation
    "sphinx.ext.autosummary",  # summary tables for modules/classes/methods etc
    "sphinx_autodoc_typehints",  # Automatically document param types
    "sphinx.ext.napoleon",  # numpy support
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",  # Link mapping to external projects
    "sphinx.ext.mathjax",  # LaTex style math
    "sphinx.ext.graphviz",  # Dependency diagrams
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "notfound.extension",
    "hoverxref.extension",
    "sphinx.ext.githubpages",
    "sphinx.ext.doctest",  # Doctest
    "myst_parser",  # MyST parser
    "nbsphinx",  # Jupyter notebook support
]
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "matplotlib": ("https://matplotlib.org", None),
}

if os.environ.get("READTHEDOCS") == "True":
    nbsphinx_execute = "never"
else:
    nbsphinx_execute = "always"

# Controls when a cell will time out (defaults to 30; use -1 for no timeout):
nbsphinx_timeout = 1000

# render type annotations as parameter types and return types.
autodoc_typehints = "description"

# -- Options for autosummary and autodoc -------------------------------------------------

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}
html_show_sourcelink = (
    False  # Remove 'view source code' from top of page (for html, not python)
)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable imports for sphinx_autodoc_typehints
nbsphinx_allow_errors = True  # Continue through Jupyter errors
# autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
add_module_names = False  # Remove namespaces from class/method signatures

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for Texinfo output -------------------------------------------

myst_update_mathjax = False

# -- Options for Sphinx-autoapi output -------------------------------------------

# autoapi_type = "python"
# autoapi_dirs = ["../satkit/"]
# autoapi_file_patterns = ["*.py"]
# autoapi_options = [
#     "members",  # Display children of an object
#     "inherited-members",  # Display children of an object that have been inherited from a base class.
#     "undoc-members",  # Display objects that have no docstring
#     "show-inheritance",  # Display a list of base classes below the class signature.
#     "show-module-summary",  # include autosummary directives in generated module documentation.
#     # "special-members", # special objects: __foo__
# ]
# autoapi_ignore = [
#     "test*",  # Ignore tests
# ]
# autoapi_add_toctree_entry = True  # Generate autoapi index page

# -- Options for hoverxref -------------------------------------------
hoverxref_auto_ref = True
hoverxref_mathjax = True
hoverxref_intersphinx = [
    "numpy",
    "scipy",
    "matplotlib",
]
