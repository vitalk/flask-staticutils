#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Flask-staticutils
~~~~~~~~~~~~~~~~~

Flask extension that provides a simple way to add revision to your app static
assets.
"""
from setuptools import setup


setup(
    name='flask-staticutils',
    version='0.2',
    license='MIT',
    author='Vital Kudzelka',
    author_email='vital.kudzelka@gmail.com',
    description='Simple way to add revision info to app static assets.',
    long_description=__doc__,
    packages=[
        'flaskext',
        'flaskext.staticutils'
    ],
    namespace_packages=['flaskext'],
    install_requires=['Flask'],
    tests_require=['Attest'],
    test_loader='attest:auto_reporter.test_loader',
    test_suite='tests.suite',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
