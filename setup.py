#!/usr/bin/env python
# coding: utf-8
import io
import os
import re

from setuptools import setup

install_requires = [
    'sphinx',
    'sphinx-py3doc-enhanced-theme'
]


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(r':[a-z]+:`~?(.*?)`', r'``\1``', fd.read())


setup(
    # --- identity
    name='tyran_axilane',
    version='0.1.0',

    # --- description
    description="Le Tyran d'axilane - Michel Grimaud - ebook",
    long_description=u"{readme}\n{changes}".format(readme=read("README.rst"), changes=read("CHANGES.rst")),
    author=u'Laurent LAPORTE',
    author_email=u'tantale.solutions@gmail.com',
    url='https://tantale.github.io/tyran_axilane/',
    license="MIT",
    platforms=['posix', 'nt'],
    keywords='epub',
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],

    # --- packaging
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=True,
)
