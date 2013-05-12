# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of nicezmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from setuptools import setup

setup(

    name = "nicezmq",
    version = "0.1.1",

    install_requires = [
        "pyzmq==13.1.0",
    ],

    tests_require = [
        "virtualenv==1.9.1",
        "tox==1.4.3",
        "nose==1.3.0",
        "mock==1.0.1",
        "coverage==3.6",
    ],

    py_modules = [
        "nicezmq",
    ],
    
    author = "Robin Kåveland Hansen",
    description = "Nicer interface to pyzmq.",

    license = "BSD",
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking",
    ],
)