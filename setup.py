from setuptools import setup

setup(
    name='sesam',
    version='0.0.2',
    packages=['sesam'],
    package_data={
        'sesam': ['wsdl/*.wsdl']
    },
    url='https://github.com/ovidner/python-sesam',
    license='MIT',
    author='Olle Vidner',
    author_email='olle@vidner.se',
    description='',
    install_requires=[
        'zeep'
    ]
)
