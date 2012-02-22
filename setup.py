import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='logging-config',
      version='1.0.1',
      description="A wrapper class for the Python standard logging module",
      long_description=read('README.md'),
      author="Gavin M. Roy",
      author_email="gmr@myyearbook.com",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Logging',
          'License :: OSI Approved :: BSD License',
          ],
      url="https://github.com/gmr/logging-config",
      tests_require=['mock'],
      py_modules = ['logging_config'],
      zip_safe=True)

