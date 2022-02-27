import ast
import re
from setuptools import find_packages, setup

# version parsing from __init__ pulled from Flask's setup.py
# https://github.com/mitsuhiko/flask/blob/master/setup.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("evident/__init__.py", "rb") as f:
    hit = _version_re.search(f.read().decode("utf-8")).group(1)
    version = str(ast.literal_eval(hit))

q2_cmds = ["q2-evident=evident.q2.plugin_setup:plugin"]

classes = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: BSD License
    Topic :: Software Development :: Libraries
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split("\n") if s]

description = "Effect size calculations for microbiome diversity data."

setup(
    name="evident",
    author="Gibraan Rahman",
    author_email="grahman@eng.ucsd.edu",
    description=description,
    url="https://github.com/gibsramen/evident",
    version=version,
    license="BSD-3-Clause",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "statsmodels",
        "scikit-bio",
        "matplotlib",
        "seaborn"
    ],
    classifiers=classifiers,
    extras_require={"dev": ["pytest", "pytest-cov", "flake8"]},
    entry_points={"qiime2.plugins": q2_cmds},
    package_data={"evident": ["citations.bib"]}
)
