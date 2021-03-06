#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""
import socket
import socketserver
import sys
import os
import time
import hashlib

from hashlib import md5
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

if len(sys.argv) != 2:
        sys.exit('Usage :python3 server.py config ')

methods_client = 'REGISTER, INVITE, BYE, ACK'

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

    def startElement(self, name, atributos):
        dicc = {}
        if name in self.atributos:
            for att in self.atributos[name]:
                dicc[att] = atributos.get(att, '')
            self.array_atributos.append([name, dicc])

    def get_att(self):
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
def EncryptPass(nonce, passwd, encoding='utf-8'):

    Encrypt_Password = hashlib.md5()
    Encrypt_Password.update(bytes(nonce, encoding))
    Encrypt_Password.update(bytes(passwd, encoding))
    Encrypt_Password.digest()
    return Encrypt_Password.hexdigest()

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

    def ConnectionRefused_log(self):
        log_write = open(self.file, 'a')
        log_write.write('Error: No server listening at '+ SERVER_Proxy+ 'port ' + str(PORT_Proxy))
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

    dest_RTPport_Array =[]
    def handle(self):
        """handle."""

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if len(line) == 0:
                break

            receive_array = line.decode('utf-8').split()
            print(receive_array)

            if 'INVITE' in receive_array:

                    dest_ip = receive_array[7]
                    dest_RPTport = receive_array[11]
                    self.dest_RTPport_Array.append(receive_array[11])
                    Loggin.receive(dest_ip, dest_RPTport, str(line))
                    print(dest_ip)
                    print(dest_RPTport)
                    mess = 'SIP/2.0 100 Trying' + ' SIP/2.0 180 Ringing '+ ' SIP/2.0 200 OK\r\n\r\n'
                    mess += 'Content-Type: application/sdp\r\n\r\n'
                    mess += 'v=0\r\n' + 'o=' + username + ' ' + uaserv_ip + ' \r\n'
                    mess += 's=sesion\r\n' + 't=0\r\n'
                    mess += 'm=audio ' + audio_port + ' RTP\r\n\r\n'
                    self.wfile.write(bytes(mess, 'utf-8'))
                    Loggin.sent_to(dest_ip, dest_RPTport, mess)

            if 'ACK' in receive_array:

                    cvlc = 'cvlc rtp://@' + uaserv_ip + ':' + self.dest_RTPport_Array[0]
                    print('Ejecutando... ', cvlc)
                    os.system(cvlc)
                    RTP = './mp32rtp -i ' + uaserv_ip + ' -p '
                    RTP += self.dest_RTPport_Array[0] + " < " + audio
                    print('Ejecutando... ', RTP)
                    os.system(RTP)
                    Loggin.sent_to(uaserv_ip, self.dest_RTPport_Array[0], 'enviado RTP')


            if 'BYE' in receive_array:

                    mess = 'SIP/2.0 200 OK\r\n\r\n'
                    self.wfile.write(bytes(mess, 'utf-8'))



if __name__ == "__main__":

    try:
            xml_config = sys.argv[1]
            client_tags = ReadXmlClient(xml_config)
            username = client_tags[0][1]['username']
            print('starting client: ' + username)
            passwd = client_tags[0][1]['passwd']
            uaserv_ip = client_tags[1][1]['ip']
            uaserv_port = int(client_tags[1][1]['puerto'])
            audio_port = (client_tags[2][1]['puerto'])
            SERVER_Proxy = client_tags[3][1]['ip']
            PORT_Proxy = int(client_tags[3][1]['puerto'])
            file_log = client_tags[4][1]['path']
            audio = client_tags[5][1]['path']

            Loggin = Client_Log(file_log)
            Loggin.Begin_client()
            serv = socketserver.UDPServer((uaserv_ip, uaserv_port), SIPRegisterHandler)
            serv.serve_forever()

    except ConnectionRefusedError:
        Loggin.ConnectionRefused_log()
        sys.exit('Error: No server listening at '+ SERVER_Proxy+ ' port ' + str(PORT_Proxy))
    except KeyboardInterrupt:
        print("client finsh")
        sys.exit()
    except KeyboardInterrupt:
        print('servidor finalizado')
