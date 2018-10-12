#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
from setuptools import setup, find_packages

with io.open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

install_requires = ['six']

native_requires = ['regex']

setup_requires = ['pytest-runner']

dev_require = ['pytest', 'zest.releaser[recommended]', 'pylint', 'tox']

tests_require = ['pytest']

with io.open('rebulk/__version__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]$', f.read(), re.MULTILINE).group(1)

args = dict(name='rebulk',
            version=version,
            description='Rebulk - Define simple search patterns in bulk to perform advanced matching on any string.',
            long_description=readme,
            # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
            classifiers=['Development Status :: 5 - Production/Stable',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Developers',
                         'Programming Language :: Python :: 2',
                         'Programming Language :: Python :: 2.7',
                         'Programming Language :: Python :: 3',
                         'Programming Language :: Python :: 3.4',
                         'Programming Language :: Python :: 3.5',
                         'Programming Language :: Python :: 3.6',
                         'Programming Language :: Python :: 3.7',
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
            setup_requires=setup_requires,
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
