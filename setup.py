# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.md') as f:
    long_description = f.read()

requirements = ['pyserial', 'colorama', 'click']

setup_requirements = ['wheel']


setup(name='terminal-s',
      version='0.1.0',
      description='A super simple serial terminal',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Yihui Xiong',
      author_email='yihui.xiong@hotmail.com',
      url='https://github.com/makerdiary/terminal-s',
      entry_points={
          'console_scripts': [
              'terminal-s=terminal_s.terminal:main'
          ],
      },
      packages=['terminal_s'],
      include_package_data=False,
      install_requires=requirements,
      zip_safe=True)
