#!/usr/bin/env python
# coding=utf-8
"""The pydatarecognition installer."""
import os
import sys

try:
    from setuptools import setup
    from setuptools.command.develop import develop

    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup

    HAVE_SETUPTOOLS = False


def main():
    try:
        if "--name" not in sys.argv:
            print(logo)
    except UnicodeEncodeError:
        pass
    # with open(os.path.join(os.path.dirname(__file__), "README.rst"), "r") as f:
    #     readme = f.read()
    skw = dict(
        name="pydatarecognition",
        description="A structured data content management system for published "
                    "scientific papers",
        long_description="A collaboration between the International Union of "
                         "Crystallography and the Billinge group at Columbia "
                         "University in the City of New York, USA.",
        license="BSD-3-clause",
        version='0.1.0',
        author="Martin Karlsen, Berrak Ozer, Simon J. L. Billinge",
        maintainer="Simon Billinge",
        author_email="sb2896@columbia.edu",
        url="https://github.com/billingegroup/pydatarecognition",
        platforms="Cross Platform",
        classifiers=["Programming Language :: Python :: 3"],
        packages=["pydatarecognition"],
        package_dir={"pydatarecognition": "pydatarecognition"},
        package_data={
             "pydatarecognition": [
            #     "templates/*",
            #     "static/*.*",
            #     "static/img/*.*",
            #     "*.xsh",
            ]
        },
        scripts=["scripts/pydatarecognition","scripts/pydr"],
        zip_safe=False,
    )
    if HAVE_SETUPTOOLS:
        skw["setup_requires"] = []
        # skw['install_requires'] = ['Jinja2', 'pymongo']
    setup(**skw)


logo = """
"""

if __name__ == "__main__":
    main()