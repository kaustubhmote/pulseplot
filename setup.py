#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["numpy", "matplotlib"]
test_requirements = ["pytest>=3"]

setup(
    name="pulseplot",
    description="A module to draw pulse-timing diagrams using Python/Matplotlib",
    version="0.1",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Kaustubh R. Mote",
    author_email="kaustubh@gmail.com",
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(include=["pulseplot"]),
    setup_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/kaustubhmote/pulseplot",
    zip_safe=False,
)
