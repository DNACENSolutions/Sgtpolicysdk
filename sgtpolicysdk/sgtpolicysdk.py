"""dna_services.py

Notes:
    Column size maintained throughout the file is 120 columns.
"""
__author__ = 'Pawan Singh <pawansi@cisco.com>'
__copyright__ = 'Copyright 2022, Cisco Systems'

import json
from client_manager import DnacClientManager
import time
import logging

logger = logging.getLogger("ClientManager")
log = logger

class SgtPolicySdk(DnacClientManager):
    pass