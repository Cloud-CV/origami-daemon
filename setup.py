#!/usr/bin/env python

from setuptools import setup, find_packages

PROJECT = "cv_origami"

with open('README.md') as readme_file:
    README = readme_file.read()

install_requires = [
  'click==6.7',
  'flask==1.0.2 ',
  'requests==2.18.4',
  'tornado==5.0.2',
  'six==1.11.0',
]

setup(
  name=PROJECT,
  version='0.1',

  description='Utility daemon to manage and deploy demos on Cloud-CV servers.',
  long_description=README,

  author='CloudCV Team',
  author_email='team@cloudcv.org',
  url='https://github.com/Cloud-CV/origami-daemon',
  packages=find_packages(exclude=['tests']),
  include_package_data=True,

  download_url='https://github.com/Cloud-CV/origami-daemon',

  install_requires=install_requires,
  classifiers=[
    'Development Status :: 1 - Alpha',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Intended Audience :: Developers',
    'Environment :: Console',
  ],

  entry_points="""
    [console_scripts]
    cv_origami = cv_origami.main:main
    """,

  zip_safe=False,
)
