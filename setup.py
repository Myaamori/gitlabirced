#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'irc', 'pyyaml', 'requests']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Pedro Alvarez Piedehierro",
    author_email='pedro@alvarezpiedehierro.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="IRC bot that connects with your GitLab projects",
    entry_points={
        'console_scripts': [
            'gitlabirced=gitlabirced.cli:main',
        ],
    },
    install_requires=requirements,
    python_requires='>=3',
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='gitlabirced',
    name='gitlabirced',
    packages=find_packages(include=['gitlabirced']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/palvarez89/gitlabirced',
    version='0.2.3',
    zip_safe=False,
)
