#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.5.9'
__author__ = 'Ellison Leão'
__license__ = 'MIT'

# flake8: noqa
try:
    from shorteners import Shortener, Shorteners
except ImportError:
    from .shorteners import Shortener, Shorteners
