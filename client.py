#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""
import socket
import socketserver

import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

if len(sys.argv) != 4:
        sys.exit('Usage :python3 uaclient.py config method option')

xml_config = sys.argv[1]

if os.path.exists(xml_config):
    method = str.upper(sys.argv[2])
    option = str.upper(sys.argv[3])
else:
    sys.exit('fichero XML no encontrado')

class XMLHandlerClient(ContentHandler):

    def __init__(self):     # Declaramos las listas de los elementos
        self.list_element = []
        self.element = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

    def startElement(self, name, element):   # Signals the start of an element in non-namespace mode.
        dicc = {}
        if name in self.element:
            for elment in self.element[name]:
                dicc[elment] = element.get(elment, '')
            self.list_element.append([name, dicc])

    def get_att(self):      # Devuelve la lista con elementos encontrados
        return self.list_element

def ReadXmlClient(xml_config):


    try:

        parser = make_parser()
        Handler = XMLHandlerClient()
        parser.setContentHandler(Handler)
        parser.parse(open(xml_config))
        configtags = Handler.get_att()

    except FileNotFoundError:
        sys.exit('File not found')

    return configtags

if __name__ == "__main__":

    xml_config = sys.argv[1]
    client_tags = ReadXmlClient(xml_config)
    print(client_tags)
