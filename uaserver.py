import os
import sys
import time
import socket
import socketserver

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from proxy_registrar import XMLHandler, LOG, sip_mess

usage_error = 'usage error: python3 server.py <file.xml>'
methods_allowed = 'invite', 'ack', 'bye'
att = {'account': ['username', 'passwd'],
       'uaserver': ['ip', 'puerto'],
       'rtpaudio': ['puerto'],
       'regproxy': ['ip', 'puerto'],
       'log': ['path'],
       'audio': ['path']}
