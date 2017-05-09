from setuptools import setup

setup(
    name='sesam',
    version='1.0.0',
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
        'zeep==1.3.*'
    ]
)
