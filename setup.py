#!/usr/bin/env python

import akcli
from setuptools import setup

setup(name='akcli',
    version=akcli.__version__,
    description='Akamai CLI tool written in Python',
    author="Seth Miller",
    author_email='seth@sethmiller.me',
    url='https://github.com/iamseth/akcli',
    packages=['akcli',],
    scripts=['bin/akcli'],
    keywords = ['akamai', 'dns', 'cli', 'client'],
    install_requires=[
                      'requests>=2.0',
                      'edgegrid-python>=1.0.9',
                      'click>=5.1',
    ],
)
