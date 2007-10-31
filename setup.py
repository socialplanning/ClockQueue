from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ClockQueue',
      version=version,
      description="ClockQueue is a library that provides some basic classes for creating asyncronous job queues for use with ClockServer",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ClockServer async zope2 Five',
      author='whit@openplans.org',
      author_email='whit@openplans.org',
      url='http://openplans.org/projects/opencore',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
