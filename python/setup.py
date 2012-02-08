#!/usr/bin/env python

from distutils.core import setup

setup(name='niml',
      version='0.12.1',
      description='Python niml parser',
      author='Christophe Eymard',
      author_email='christophe.eymard@ravelsoft.com',
      url='http://niml.github.com/',
      packages=['niml'],
      scripts=['scripts/niml'],
      requires=['pwpeg']
     )
