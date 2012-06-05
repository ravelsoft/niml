#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name             = 'niml',
    version          = '0.12.7',
    description      = 'Python niml parser',
    author           = 'Christophe Eymard',
    author_email     = 'christophe.eymard@ravelsoft.com',
    url              = 'http://niml.github.com/',
    packages         = ['niml'],
    scripts          = ['scripts/niml'],
    install_requires = ['pwpeg']
)
