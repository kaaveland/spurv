from setuptools import setup

setup(
    name = "nicezmq",
    version = "0.1.1",

    install_requires = [
#        "argparse==1.2.1",
#        "distribute==0.6.24"
#        "gevent==0.13.8",
#        "greenlet==0.4.0",
        "pyzmq==13.1.0",
#wsgiref==0.1.2
    ],
    tests_require = [
        "virtualenv==1.9.1",
        "tox==1.4.3",
        "nose==1.3.0",
        "mock==1.0.1",
        "coverage==3.6"
    ],
    py_modules = [
        "nicezmq"
    ],
    
    author = "Robin K. Hansen",
    description = "Nicer interface to pyzmq.",
    
)
