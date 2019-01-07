import os
import sys
import time
import socket

from xml.sax import make_parser
from proxy_registrar import XMLHandler, LOG, get_digest

usage_error = 'usage error: python3 client.py <file.xml> <method> <option>'
methods_allowed = 'register, invite, bye, ack'
att = {'account': ['username', 'passwd'],
       'uaserver': ['ip', 'puerto'],
       'rtpaudio': ['puerto'],
       'regproxy': ['ip', 'puerto'],
       'log': ['path'],
       'audio': ['path']}
