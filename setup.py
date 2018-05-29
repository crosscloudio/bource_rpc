from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bourne-rpc',

    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='JSON RPC library with the focus for IPC',
    long_description=long_description,

    url='https://github.com/pypa/sampleproject',

    # Author details
    author='The Python Packaging Authority',
    author_email='pypa-dev@googlegroups.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='rpc json development',

    packages=find_packages(exclude=['docs', 'tests']),

    # $ pip install -e .[test]
    extras_require={
        'test': ['pytest', 'pytest-cov'],
    },
)
