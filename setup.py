"""
Setup for the Django Redmine app.
"""
from setuptools import setup, find_packages


VERSION = __import__('django_redmine').__version__

from distutils.command.sdist import sdist
from distutils.command.build import build
import os

def write_version_file():
    f = open("django_redmine/version.py", "w")
    f.write('__version__ = %s\n' % (VERSION,))
    f.close()

def remove_version_file():
    os.remove("django_redmine/version.py")

class sdist_version(sdist):

    def run(self):
        write_version_file()
        sdist.run(self)
        remove_version_file()

class build_version(build):

    def run(self):
        write_version_file()
        build.run(self)
        remove_version_file()


setup(
    name = "django-redmine",
    version = VERSION,
    description = u"Django Redmine",
    keywords = u"django redmine",
    license = "BSD",
    author = u"Ryan Lee",
    author_email = u"ryanlee@zepheira.com",
    url = "https://github.com/zepheira/django-redmine",
    packages = find_packages(),
    include_package_data=True,
    cmdclass = {'sdist': sdist_version, 'build': build_version}
)
