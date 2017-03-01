import codecs
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    """Open a related file and return its content."""
    with codecs.open(os.path.join(here, filename), encoding='utf-8') as f:
        content = f.read()
    return content


README = read_file('README.rst')
CHANGELOG = CONTRIBUTORS = ''

REQUIREMENTS = []

setup(name='imt-digiposte-woleet',
      version='0.1.0.dev0',
      description='Create students accounts @ digiposte and upload diploma and woleet receipt.',
      long_description=README + "\n\n" + CHANGELOG + "\n\n" + CONTRIBUTORS,
      license='Apache License (2.0)',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: Implementation :: CPython",
          "License :: OSI Approved :: Apache Software License"
      ],
      keywords="web digiposte blockchain anchoring",
      author='Rémy Hubscher',
      author_email='hubscher.remy@gmail.com',
      url='https://github.com/Natim/imt-digiposte-woleet',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS)
