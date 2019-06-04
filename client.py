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


    try:
        parser = make_parser()
        Handler = XMLHandlerClient()
        parser.setContentHandler(Handler)
        parser.parse(open(xml_config))
        configtags = Handler.get_att()

    except FileNotFoundError:
        sys.exit('fichero XML no encontrado')

    return configtags

class Client_Log:

    def __init__(self, file_log):

        if not os.path.exists(file_log):
            os.system('touch ' + file_log)
        self.file = file_log


    def Begin_client(self):
        Hora_inicio = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        mensaje_inicio = Hora_inicio + ' Starting...\n'
        log_write = open(self.file, 'a')
        log_write.write(mensaje_inicio)
        log_write.close()



if __name__ == "__main__":

    try:
            xml_config = sys.argv[1]
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
            Loggin = Client_Log(file_log)
            Loggin.Begin_client()


            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((SERVER_Proxy, PORT_Proxy))

                print('RECIBIDO EN SOCKET MENSAJE:')

    except IndexError:
        print('SIP/2.0 404 User Not Found\r\n\r\n')
        sys.exit()


    except ConnectionRefusedError:
        print("No server listening at " + SERVER_Proxy + ' port ' + str(PORT_proxy))
        sys.exit()

    except KeyboardInterrupt:
        print("client finsh")
        sys.exit()
