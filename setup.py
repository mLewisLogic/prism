#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2012 Mike Lewis

from setuptools import setup, find_packages

import prism
version = str(prism.__version__)

setup(name=u'prism',
      version=version,
      author='Mike Lewis',
      author_email='mike@cleverkoala.com',
      url='http://github.com/mLewisLogic/prism',
      description='image/thumbnail processor that stores results in AWS S3',
      long_description=open('./readme.md', 'r').read(),
      download_url='http://github.com/mLewisLogic/prism/tarball/master',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'License :: OSI Approved :: MIT License',
          ],
      packages=find_packages(),
      license='MIT License',
      keywords='image thumbnail aws s3',
      include_package_data=True,
      zip_safe=True,
      )
