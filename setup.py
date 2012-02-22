import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='logging-config',
      version='1.0.0',
      description="A wrapper class for the Python standard logging module",
      long_description=read('README.md'),
      author="Gavin M. Roy",
      author_email="gmr@myyearbook.com",
      url="https://github.com/gmr/logging-config",
      tests_require=['mock'],
      py_modules = ['logging_config'],
      zip_safe=True)
