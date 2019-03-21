#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Copyright (c) 2018, The Evident Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from setuptools import setup
from glob import glob
import re
import ast

# version parsing from __init__ pulled from Flask's setup.py
# https://github.com/mitsuhiko/flask/blob/master/setup.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('evident/__init__.py', 'rb') as f:
    hit = _version_re.search(f.read().decode('utf-8')).group(1)
    __version__ = str(ast.literal_eval(hit))


classes = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 3.5
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
"""

long_description = ("Evident")

classifiers = [s.strip() for s in classes.split('\n') if s]

setup(name='evident',
      version=__version__,
      long_description=long_description,
      license="BSD",
      description='Evident',
      author="Evident development team",
      author_email="antgonza@gmail.com",
      url='https://github.com/biocore/evident',
      test_suite='nose.collector',
      packages=['evident', 'evident.tests'],
      package_data={'evident.tests.support_files': ['*']},
      scripts=glob('scripts/*'),
      extras_require={'test': ["nose >= 0.10.1", "pep8"],
                      'doc': ["Sphinx >= 1.2.2", "sphinx-bootstrap-theme"]},
      install_requires=['click', 'numpy', 'scikit-bio', 'scipy', 'joblib',
                        'seaborn', 'statsmodel'],
      classifiers=classifiers
      )
