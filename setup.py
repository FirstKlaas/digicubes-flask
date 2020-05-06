"""
Setup file for the digicubes package
"""
import json

from setuptools import setup, find_namespace_packages

def version() -> str:
    """
    Returns the current version of the digicubes server
    """
    with open("digicubes_flask/version.json") as f:
        data = json.load(f)
        return ".".join(str(n) for n in data["version"])

def requirements() -> list:
    """
    Returns an array of required packages für the server.
    """
    return open("requirements.txt", "rt").read().splitlines()

setup(
    # Application name:
    name="digicubes-flask",
    # Version number:
    version=version(),
    # Application author details:
    author="Klaas Nebuhr, Marion Nebuhr",
    author_email="klaas.nebuhr@gmail.com",
    # License
    license="Apache License Version 2.0",
    # Packages
    packages=find_namespace_packages(
        include=["digicubes*"]
    ),
    zip_safe=False,
    # Include additional files into the package
    include_package_data=True,
    # Details
    description="A digicubes flask addon",
    long_description=open("README.rst", "r").read(),
    long_description_content_type='text/x-rst',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: AsyncIO",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords=(
        "flask digicubes api learning platform"
    ),
    # Dependent packages (distributions)
    install_requires=requirements(),
)
