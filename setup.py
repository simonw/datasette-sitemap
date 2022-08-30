from setuptools import setup
import os

VERSION = "1.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-sitemap",
    description="Generate sitemap.xml for Datasette sites",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-sitemap",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-sitemap/issues",
        "CI": "https://github.com/simonw/datasette-sitemap/actions",
        "Changelog": "https://github.com/simonw/datasette-sitemap/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["datasette_sitemap"],
    entry_points={"datasette": ["sitemap = datasette_sitemap"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio", "datasette-block-robots"]},
    python_requires=">=3.7",
)
