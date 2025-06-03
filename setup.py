"""
Minimal setup.py file for backward compatibility.
Modern Python projects should use pyproject.toml instead.
"""

from setuptools import setup

setup(
    name="zcrawl",
    version="0.0.1",
    description="Advanced web crawling and scraping desktop application",
    author="Yusef Ulum",
    author_email="yusefulum@gmail.com",
    packages=["zcrawl"],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.4.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "colorama>=0.4.5",
        "lxml>=4.9.0",
    ],
)
