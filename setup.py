import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-moj-auth',
    version='0.1',
    packages=['moj_auth', 'moj_auth.tests'],
    include_package_data=True,
    license='BSD License',
    description='Authentication backend for MoJ OAuth services',
    long_description=README,
    install_requires=['Django==1.8.3', 'slumber==0.7.1', 'requests-oauthlib==0.5.0'],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: MoJ Developers',
    ],
)
