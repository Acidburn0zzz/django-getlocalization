#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-getlocalization',
    version='0.1',
    author='Get Localization',
    author_email='support@getlocalization.zendesk.com',
    url='http://github.com/getlocalization/django-getlocalization',
    description = 'Synchronize localization files with Get Localization service',
    packages=find_packages(exclude="example_project"),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
