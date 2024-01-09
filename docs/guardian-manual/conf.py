# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
import sys

# sys.path.insert(0, os.path.abspath('.'))
from datetime import date

# -- Project information -----------------------------------------------------


def read_version_from_ci() -> str:
    """Read the version for the documentation from the pipeline definition

    To not maintain the documentation version in different places, just define
    at one place and use it in different places.

    The documentation version influences the version shown in the content of
    the document and the path of the published documentation.

    :returns: The version number for the documentation as defined in the CI/CD
        pipeline.

    :rtype: str
    """

    import yaml

    with open("../../.gitlab-ci.yml", "r") as f:
        ci = yaml.safe_load(f)
        return ci.get("variables", {"DOC_TARGET_VERSION": "1.0"}).get(
            "DOC_TARGET_VERSION"
        )


release = read_version_from_ci()
version = release

project = "Guardian Manual {}".format(release)
copyright = "{}, Univention GmbH".format(date.today().year)
author = "Univention GmbH"
language = "en"

html_title = project

# The doc_basename must match the documents root directory name on the public
# target location. Otherwise the PDF link on the overview page will point to
# the wrong file.
doc_basename = "guardian-manual"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_copybutton",
    "sphinxcontrib.spelling",
    "univention_sphinx_extension",
    "sphinx_sitemap",
    "sphinx_last_updated_by_git",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "uv-ucsschool-id-connector": (
        "https://docs.software-univention.de/ucsschool-id-connector/",
        None,
    ),
    "uv-dev-ref": (
        "https://docs.software-univention.de/developer-reference/latest/en/",
        None,
    ),
    "uv-keycloak-app": (
        "https://docs.software-univention.de/keycloak-app/latest/",
        None,
    ),
    "uv-ucs-manual": (
        "https://docs.software-univention.de/manual/latest/en/",
        None,
    ),
    "uv-app-center": (
        "https://docs.software-univention.de/app-center/latest/en/",
        None,
    ),
    "loguru": (
        "https://loguru.readthedocs.io/en/stable/",
        None,
    ),
}

# For more configuration options of Sphinx-copybutton, see the documentation
# https://sphinx-copybutton.readthedocs.io/en/latest/index.html
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOT"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "univention_sphinx_book_theme"
html_theme_options = {
    "pdf_download_filename": f"{doc_basename}.pdf",
    "show_source_license": True,
    "typesense_search": True,
    "typesense_document": doc_basename,
    "typesense_document_version": version,  # or "latest"
    "univention_docs_deployment": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


numfig = True


suppress_warnings = ["git.too_shallow"]
git_last_updated_timezone = "Europe/Berlin"

if "spelling" in sys.argv:
    spelling_lang = "en"
    spelling_show_suggestions = True
    spelling_word_list_filename = ["spelling_wordlist"]

root_doc = "contents"

latex_engine = "lualatex"
latex_show_pagerefs = True
latex_show_urls = "footnote"
latex_documents = [(root_doc, f"{doc_basename}.tex", project, author, "manual", False)]
latex_elements = {
    "papersize": "a4paper",
    "babel": "\\usepackage{babel}",
}

# Sitemap, see https://github.com/jdillard/sphinx-sitemap
sitemap_url_scheme = "{version}{lang}{link}"
html_baseurl = ""


# Configure Univention feedback link
# See https://git.knut.univention.de/univention/documentation/univention_sphinx_extension#univention_feedback

# Deactivated per default. To activate, set it to True.

univention_feedback = True
univention_doc_basename = doc_basename
univention_pdf_show_source_license = True
