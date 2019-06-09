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
import socket

from hashlib import md5
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from datetime import datetime, date, timedelta

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

def time_now():

    #return time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
    return time.time()

def EncryptPass(nonce, passwd, encoding='utf-8'):

    Encrypt_Password = hashlib.md5()
    Encrypt_Password.update(bytes(nonce, encoding))
    Encrypt_Password.update(bytes(passwd, encoding))
    Encrypt_Password.digest()
    return Encrypt_Password.hexdigest()

class Proxy_Log:

    def __init__(self, file_log):

        if not os.path.exists(file_log):
            os.system('touch ' + file_log)
        self.file = file_log
        Hora_inicio = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        mensaje_inicio = Hora_inicio + ' Starting proxy_server...\n'
        log_write = open(self.file, 'a')
        log_write.write(mensaje_inicio)
        log_write.close()


    def sent_to(self, ip, port, send_mess):
        Hora_inicio = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        mess = Hora_inicio + ' Send to ' + ip + ':' + str(port) + ': '
        mess += send_mess.replace('\r\n', ' ') + '\r\n'
        log_write = open(self.file, 'a')
        log_write.write(mess)
        log_write.close()

    def receive(self, ip, port, send_mess):
        Hora_inicio = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        mess = Hora_inicio + ' recived from' + ip + ':' + str(port) + ': '
        mess += send_mess
        log_write = open(self.file, 'a')
        log_write.write(mess)
        log_write.close()


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    dicc = {}
    Passw_dicc = {}
    def register2json(self):
        """intamos abris j.son si no existe creamos en excep"""
        try:
            with open('registered.json', 'r') as json_file:
                self.dicc = json.load(json_file)
        except:
            with open('registered.json', 'w') as json_file:
                json.dump(self.dicc, json_file, indent=2)


    def ReadPasswords(self):

        with open('passwords.txt', 'r') as passwords_file:
            for line in passwords_file:
                user = (line.split()[0])
                password = str(line.split()[1])

                self.Passw_dicc[user] = (password)


    def handle(self):
        """handle."""

        self.register2json()
        self.ReadPasswords()
        print(self.Passw_dicc)


        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if len(line) == 0:
                break

            receive_array = line.decode('utf-8').split()
            print(receive_array)
            if 'INVITE' in receive_array:
                username_dest =  receive_array[1].split(':')[1]
                username = receive_array[6].split('=')[1]
                print(username_dest)
                print(username)

                print(receive_array[1])
                if username_dest in self.dicc:
                    print('hola')
                    print(username_dest)
                    dest_ip = self.dicc.get(username_dest).split()[0]
                    dest_ip = dst_ip.split(':')[1].split()[0]
                    dest_port = self.dicc.get(username_dest).split()[1]
                    print(dst_ip)
                    print(dst_port)
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                            my_socket.connect((dest_ip, int(dest_port)))
                            my_socket.send(bytes(line, 'utf-8'))
                            data = sck.recv(1024)
                            line = data.decode("utf-8")
                            if '180' in receive_array:
                                self.wfile.write(bytes(str(line), 'utf-8'))
                    except:
                        print('user not found')


            if 'REGISTER' in receive_array:
                username =  receive_array[1].split(':')[1]
                user_rtp_port = receive_array[1].split(':')[2]
                expires = float(receive_array[3].split(':')[1])
                expired = float(receive_array[3].split(':')[1]) + time_now()
                ip = self.client_address[0]
                Loggin.receive(ip, user_rtp_port, str(line))
                if username in self.dicc:
                        self.dicc[username] = ('Ip:' + ip + user_rtp_port + ' Registered: ' + str(expired) + str(expires))
                        mess ='SIP/2.0 200 OK\r\n\r\n'
                        self.wfile.write(bytes(mess, 'utf-8'))
                        print('user ' + username + ' log in')
                        if expires == 0:
                            del self.dicc[username]
                else:
                    if 4  == len(receive_array):
                        passwd = self.Passw_dicc[username]
                        print(passwd)
                        Encr_Pass = EncryptPass(username, passwd)
                        print(Encr_Pass)
                        mess ='SIP/2.0 401 Unauthorized WWW-Authenticate: Digest nonce= ' + Encr_Pass

                        self.wfile.write(bytes(mess, 'utf-8'))
                    else:
                        if 5  == len(receive_array):
                            print(receive_array)
                            if username in self.Passw_dicc:
                                print('555555')
                                self.dicc[username] = ('Ip:' + ip + ' ' + user_rtp_port + ' Registered: ' + str(expired) + str(expires))


            with open('registered.json', 'w') as json_file:
                json.dump(self.dicc, json_file, indent=2)



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
    file_log = proxy_tags[2][1]['path']
    Loggin = Proxy_Log(file_log)
    print(client_passwords)

    serv = socketserver.UDPServer((proxy_ip, proxy_port), SIPRegisterHandler)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('servidor finalizado')

    print("Lanzando servidor UDP de eco...")
