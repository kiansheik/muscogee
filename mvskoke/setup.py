# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="mvskoke",
    version="0.1.0",
    description="Mvskoke (Creek) language tools",
    long_description=readme,
    author="Kian Sheik",
    author_email="ksheik@usp.br",
    url="https://github.com/kiansheik/muscogee",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
