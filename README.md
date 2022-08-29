# datasette-sitemap

[![PyPI](https://img.shields.io/pypi/v/datasette-sitemap.svg)](https://pypi.org/project/datasette-sitemap/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-sitemap?include_prereleases&label=changelog)](https://github.com/simonw/datasette-sitemap/releases)
[![Tests](https://github.com/simonw/datasette-sitemap/workflows/Test/badge.svg)](https://github.com/simonw/datasette-sitemap/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-sitemap/blob/main/LICENSE)

Generate sitemap.xml for Datasette sites

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-sitemap

## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-sitemap
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
