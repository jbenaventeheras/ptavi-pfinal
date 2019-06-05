#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa user agent client"""

import json
import os
import sys
import json
import time
import random
import hashlib
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from datetime import datetime, date, time, timedelta

if len(sys.argv) != 2:
    sys.exit('usage error: python3 proxy_registrar.py config')

class XMLHandlerProxy(ContentHandler):

    def __init__(self):     # Declaramos las listas de los elementos
        self.array_atributos = []
        self.atributos = {
            'server': ['name', 'ip', 'puerto'],
            'database': ['path', 'pathpassw'],
            'log': ['path']}

    def startElement(self, name, atributos):   # Signals the start of an atributos in non-namespace mode.
        dicc = {}
        if name in self.atributos:
            for att in self.atributos[name]:
                dicc[att] = atributos.get(att, '')
            self.array_atributos.append([name, dicc])

    def get_att(self):      # Devuelve la lista con elementos encontrados
        return self.array_atributos

def ReadXmlProxy(proxy_config):

    try:
        parser = make_parser()
        Handler = XMLHandlerProxy()
        parser.setContentHandler(Handler)
        parser.parse(open(proxy_config))
        configtags = Handler.get_att()

    except FileNotFoundError:
        sys.exit('fichero XML no encontrado')

    return configtags


class Proxy_Log:

    def __init__(self, file_log):

        if not os.path.exists(file_log):
            os.system('touch ' + file_log)
        self.file = file_log


    def sent_to(self, ip, port, send_mess):
        Hora_inicio = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        mess = Hora_inicio + ' Send to ' + ip + ':' + str(port) + ': '
        mess += send_mess.replace('\r\n', ' ') + '\r\n'
        log_write = open(self.file, 'a')
        log_write.write(mess)
        log_write.close()



class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    dicc = {}
    def register2json(self):
        """intamos abris j.son si no existe creamos en excep"""
        try:
            with open('registered.json', 'r') as json_file:
                self.dicc = json.load(json_file)
        except:
            with open('registered.json', 'w') as json_file:
                json.dump(self.dicc, json_file, indent=2)

    def handle(self):
        """handle."""
        self.register2json()
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if len(line) == 0:
                break
            receive_array = line.decode('utf-8').split()
            if 'REGISTER' in receive_array:
                print(receive_array)


if __name__ == "__main__":


    proxy_config = sys.argv[1]
    proxy_tags = ReadXmlProxy(proxy_config)
    print(proxy_tags)
    proxy_name = proxy_tags[0][1]['name']
    print(proxy_name)
    proxy_ip = proxy_tags[0][1]['ip']
    proxy_port = int(proxy_tags[0][1]['puerto'])
    client_register = proxy_tags[1][1]['path']
    client_passwords= proxy_tags[1][1]['pathpassw']
    print(client_passwords)

    serv = socketserver.UDPServer((proxy_ip, proxy_port), SIPRegisterHandler)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('servidor finalizado')

    print("Lanzando servidor UDP de eco...")
