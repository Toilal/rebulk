#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re

from setuptools import setup, find_packages

with io.open('CHANGELOG.md', encoding='utf-8') as f:
    changelog = f.read()

with io.open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

install_requires = []

native_requires = ['regex']

dev_require = ['pytest', 'pylint', 'tox']

tests_require = ['pytest', 'pylint']

with io.open('rebulk/__version__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

args = dict(name='rebulk',
            version=version,
            description='Rebulk - Define simple search patterns in bulk to perform advanced matching on any string.',
            long_description=readme + '\n\n' + changelog,
            long_description_content_type='text/markdown',
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=['Development Status :: 5 - Production/Stable',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Developers',
                         'Programming Language :: Python :: 3',
                         'Programming Language :: Python :: 3.7',
                         'Programming Language :: Python :: 3.8',
                         'Programming Language :: Python :: 3.9',
                         'Programming Language :: Python :: 3.10',
                         'Programming Language :: Python :: 3.11',
                         'Topic :: Software Development :: Libraries :: Python Modules'
                         ],
            keywords='re regexp regular expression search pattern string match',
            author='Rémi Alvergnat',
            author_email='toilal.dev@gmail.com',
            url='https://github.com/Toilal/rebulk/',
            download_url='https://pypi.python.org/packages/source/r/rebulk/rebulk-%s.tar.gz' % version,
            license='MIT',
            packages=find_packages(),
            include_package_data=True,
            install_requires=install_requires,
            tests_require=tests_require,
            test_suite='rebulk.test',
            zip_safe=True,
            extras_require={
                'test': tests_require,
                'dev': dev_require,
                'native': native_requires
            }
            )

setup(**args)
