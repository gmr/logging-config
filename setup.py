from setuptools import setup
long_desc = """\
A configuration wrapper class for the standard Python logging package. Since
DictConfigurator is not available until 2.7 and I still need to support 2.6,
I wanted a consistent way to handle configuration of application logging."""

setup(name='logging-config',
      version='1.0.2',
      description="A wrapper class for the Python standard logging module",
      long_description=long_desc,
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

