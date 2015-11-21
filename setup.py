#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

base_dir = path.abspath(path.dirname(__file__))

# Get the long description from the README.rst file
with open(path.join(base_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

required_packages = ['PyYAML']
required_packages_test = ['pytest', 'pytest-cov']


setup(
    name='pipeapp',
    version='0.1',
    description='Basic and Pipeline and Application classes',
    long_description=long_description,
    author='David Managadze',
    author_email='dmanagadze@gmail.com',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific / Engineering :: Bio - Informatics',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        ],
    keywords='bioinformatics pipeline',
    install_requires=required_packages,
    tests_require=required_packages_test,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'example_app = pipeapp.apps.example_app:run_from_console'
        ]
    },
    scripts=[
        'bin/start_pipeline.sh'
    ]
)
