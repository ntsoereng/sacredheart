"""Phusion Passenger entry point used by cPanel's Setup Python App."""

import os
import sys
from pathlib import Path


APPLICATION_ROOT = Path(__file__).resolve().parent
if str(APPLICATION_ROOT) not in sys.path:
    sys.path.insert(0, str(APPLICATION_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application  # noqa: E402,F401
