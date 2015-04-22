#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path
import vdf

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vdf',
    version=vdf.__version__,
    description='Library for working with Valve\'s VDF text format',
    long_description=long_description,
    url='https://github.com/rossengeorgiev/vdf-python',
    author='Rossen Georgiev',
    author_email='hello@rgp.io',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing ',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='valve keyvalue vdf tf2 dota2 csgo',
    packages=['vdf'],
    zip_safe=False,
)
