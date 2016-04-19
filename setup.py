import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-moj-auth',
    version='1.3',
    author='Ministry of Justice Digital Services',
    url='https://github.com/ministryofjustice/django-moj-auth',
    packages=['moj_auth', 'moj_auth.tests'],
    include_package_data=True,
    license='MIT',
    description='Authentication backend for MoJ OAuth services',
    long_description=README,
    install_requires=[
        'Django>=1.8',
        'slumber>=0.7',
        'requests-oauthlib>=0.5',
        'django-form-error-reporting>=0.2',
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='runtests.runtests',
    tests_require=['responses>=0.5']
)
