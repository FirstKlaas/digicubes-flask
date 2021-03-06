# pylint: disable=C0111
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'digicubes client'
copyright = '2019, Klaas Nebuhr, Marion Nebuhr' # pylint: disable=redefined-builtin
author = 'Klaas Nebuhr, Marion Nebuhr'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.httpdomain', 'sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'tortoise-orm': ('https://tortoise-orm.readthedocs.io/en/latest/', None),
    'pyjwt': ('https://pyjwt.readthedocs.io/en/latest/', None),
    'responder' : ("https://responder.readthedocs.io/en/latest/", None)
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
