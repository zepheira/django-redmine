"""
Setup for the Django Redmine app.
"""
from setuptools import setup, find_packages

setup(
    name = "django-redmine",
    version = "1.0.0",
    description = u"Django Redmine",
    keywords = u"django redmine",
    license = "BSD",
    author = u"Ryan Lee",
    author_email = u"ryanlee@zepheira.com",
    url = "https://github.com/zepheira/django-redmine",
    packages = find_packages(),
    include_package_data=True
)
