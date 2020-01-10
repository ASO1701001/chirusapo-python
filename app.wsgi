# -*- coding:utf-8 -*-

import logging
import os
import sys

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app as application
