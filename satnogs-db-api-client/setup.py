from __future__ import absolute_import, division, print_function, \
    unicode_literals

from setuptools import setup

import versioneer

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
