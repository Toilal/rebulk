#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from platform import python_implementation

import os


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

install_requires = ['six', 'regex']
if python_implementation() == 'PyPy':
    install_requires.remove('regex')  # PyPy doesn't support regex module

setup_requires=['pytest-runner']

tests_require=['pytest']

exec(open("rebulk/__version__.py").read())  # load version without importing rebulk

args = dict(name='rebulk',
            version=__version__,
            description='Rebulk - Define simple search patterns in bulk to perform advanced matching on any string.',
            long_description=README,
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=['Development Status :: 3 - Alpha',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Developers',
                         'Programming Language :: Python :: 2',
                         'Programming Language :: Python :: 2.7',
                         'Programming Language :: Python :: 3',
                         'Programming Language :: Python :: 3.3',
                         'Programming Language :: Python :: 3.4',
                         'Programming Language :: Python :: 3.5',
                         'Topic :: Software Development :: Libraries :: Python Modules'
                         ],
            keywords='re regexp regular expression search pattern string match',
            author='Rémi Alvergnat',
            author_email='toilal.dev@gmail.com',
            url='https://github.com/Toilal/rebulk/',
            download_url='https://pypi.python.org/packages/source/r/rebulk/rebulk-%s.tar.gz' % __version__,
            license='MIT',
            packages=find_packages(),
            include_package_data=True,
            setup_requires=setup_requires,
            install_requires=install_requires,
            tests_require=tests_require,
            test_suite='rebulk.test',
            )

setup(**args)
