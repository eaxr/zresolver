#!/usr/bin/env python

from distutils.core import setup


setup(name='zResolver',
      version='1.0',
      description='Test model for dns resolve',
      author='eaxr',
      author_email='',
      url='github.com/eaxr',
      packages=['zresolver'],
      data_files=[('/etc/zresolver', ['./zresolver/resolver.conf']),
                  ('/etc/systemd/system', ['./zresolver/zResolver.service']),
                  ('/var/log/zresolver', ['./zresolver/logfile.log'])]
     )
