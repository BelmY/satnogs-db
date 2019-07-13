#!/usr/bin/env python
"""WSGI module for SatNOGS DB"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.settings')

application = get_wsgi_application()
