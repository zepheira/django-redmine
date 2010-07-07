"""
Setup for the Freemix Redmine app.
"""
from setuptools import setup, find_packages

setup(
    name = "freemix-redmine",
    version = "1.0.0-dev",
    description = "Freemix Redmine",
    url = "http://foundry.zepheira.com/hg/freemix-redmine",
    packages = find_packages(),
    install_requires = [
        "freemix > 1.1"
    ]
)
