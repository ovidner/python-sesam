from setuptools import setup

setup(
    name='sesam',
    version='0.0.1',
    py_modules=['sesam'],
    url='https://github.com/ovidner/python-sesam',
    license='MIT',
    author='Olle Vidner',
    author_email='olle@vidner.se',
    description='',
    dependency_links=[
        'https://bitbucket.org/jurko/suds/get/94664ddd46a61d06862fa8fb6ba7b9e054214f57.tar.bz2#egg=suds-jurko'
    ],
    install_requires=[
        'suds-jurko'
    ]
)
