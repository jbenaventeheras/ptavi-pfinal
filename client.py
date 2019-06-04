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
        self.array_atributos = []
        self.atributos = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

    def startElement(self, name, atributos):   # Signals the start of an atributos in non-namespace mode.
        dicc = {}
        if name in self.atributos:
            for att in self.atributos[name]:
                dicc[att] = atributos.get(att, '')
            self.array_atributos.append([name, dicc])

    def get_att(self):      # Devuelve la lista con elementos encontrados
        return self.array_atributos

def ReadXmlClient(xml_config):

    xml_config = sys.argv[1]
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

    client_tags = ReadXmlClient(xml_config)
    username = client_tags[0][1]

    passwd = client_tags[0][1]['passwd']
    uaserv_ip = client_tags[1][1]['ip']
    uaserv_port = str(client_tags[1][1]['puerto'])
    audio_port = (client_tags[2][1]['puerto'])
    SERVER_Proxy = client_tags[3][1]['ip']
    PORT_Proxy = int(client_tags[3][1]['puerto'])
    file_log = client_tags[4][1]['path']
    audio = client_tags[5][1]['path']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((SERVER_Proxy, PORT_Proxy))
        data = my_socket.recv(1024)
        server_OK = data.decode('utf-8').split(' ')[-1]
        print('RECIBIDO EN SOCKET MENSAJE: ' + data.decode('utf-8')
