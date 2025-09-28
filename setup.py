from setuptools import find_packages
from setuptools import setup

setup(name='App_DISP',
      version='1.0',
      description='Data Interpreter for STELUM and PULSE',
      author='Nathan Guyot',
      packages=find_packages('.'),
      packages_dir={'','.'},
      install_requires=[
          'numpy',
          'matplotlib']
      )