# /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import socket
import random
import socketserver

from hashlib import md5
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

att = {'server': ['name', 'ip', 'puerto'],
       'database': ['path', 'passwdpath'],
       'log': ['path']}
date_log = '%Y%m%d%H%M%S'
date_reg = '%d/%m/%Y %H:%M:%S'
usage_error = 'usage error: python3 proxy.py <file.xml>'
sip_mess = {'100': 'SIP/2.0 100 Trying\r\n\r\n',
            '180': 'SIP/2.0 180 Ringing\r\n\r\n',
            '200': 'SIP/2.0 200 OK\r\n\r\n',
            '400': 'SIP/2.0 400 Bad Request\r\n\r\n',
            '401': 'SIP/2.0 401 Unauthorized\r\n\r\n',
            '404': 'SIP/2.0 404 User Not Found\r\n\r\n',
            '405': 'SIP/2.0 405 Method Not Allowed\r\n\r\n'}
