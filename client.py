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

if len(sys.argv) != 4:
        sys.exit('Usage :python3 client.py config method option')

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


if __name__ == "__main__":

    option = sys.argv[3]
    method = (sys.argv[2])
    if str.upper(method) in methods_client:
        print(method)

        try:
                xml_config = sys.argv[1]
                client_tags = ReadXmlClient(xml_config)
                username = client_tags[0][1]['username']
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
                    if str.upper(method) == 'REGISTER':
                        send_mess = method + ' sip:' + username + ':' + uaserv_port + ' SIP/2.0\r\n' + 'Expires:' + option + '\r\n\r\n'
                        my_socket.send(bytes(send_mess, 'utf-8') + b'\r\n')
                        Loggin.sent_to(uaserv_ip, uaserv_port, send_mess)
                        print('hola')
                    if str.upper(method) == 'INVITE':
                        send_mess = ' ' + method +' ' + option + ' SIP/2.0\r\n'
                        send_mess += 'Content-Type: application/sdp\r\n\r\n'
                        send_mess += 'v=0\r\n' + 'o=' + username + ' ' + uaserv_ip + ' \r\n'
                        send_mess += 's=sesion\r\n' + 't=0\r\n'
                        send_mess += 'm=audio ' + audio_port + ' RTP\r\n\r\n'
                        my_socket.send(bytes(send_mess, 'utf-8') + b'\r\n')
                        Loggin.sent_to(uaserv_ip, uaserv_port, send_mess)
                    if str.upper(method) == 'BYE':
                        send_mess = METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n\r\n'
                        my_socket.send(bytes(send_mess, 'utf-8') + b'\r\n')
                        Loggin.sent_to(self, uaserv_ip, uaserv_port, send_mess)


                    data = my_socket.recv(1024).decode('utf-8')
                    print(data)



                    if '401' in data:
                        RandomNum = data.split()[6]
                        Encr_Pass = EncryptPass(RandomNum, passwd)
                        send_mess = method + ' sip:' + username + ':' + uaserv_port + ' SIP/2.0\r\n' + 'Expires:' + option + '\r\n\r\n' + Encr_Pass
                        my_socket.send(bytes(send_mess, 'utf-8') + b'\r\n')
                        Loggin.sent_to(uaserv_ip, uaserv_port, send_mess)
                    if '180' in data:
                        print(hola)
                        mess = 'ACK' + ' sip:' + method + ' SIP/2.0\r\n\r\n'
                        my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
                        log.sent_to(proxy_ip, proxy_port, LINE)
                        data = my_socket.recv(1024)
                        print('Envio ack: ' + LINE)
                        print(data.decode('utf-8'))
                        cvlc = 'cvlc rtp://@' + uaserv_ip + ':' + aud_port_emisor
                        log.ejecutando(cvlc)
                        print('Ejecutando... ', cvlc)
                        os.system(cvlc)
                        RTP = './mp32rtp -i ' + uaserv_ip + ' -p '
                        RTP += aud_port_emisor + " < " + audio
                        log.ejecutando(RTP)
                        print('Ejecutando... ', RTP)
                        os.system(RTP)
                    if '200' in data:
                        print('ok received')
                    if '400' in data:
                        print('bad request received')

        except ConnectionRefusedError:
            Loggin.ConnectionRefused_log()
            sys.exit('Error: No server listening at '+ SERVER_Proxy+ ' port ' + str(PORT_Proxy))
        except KeyboardInterrupt:
            print("client finsh")
            sys.exit()
    else:
        sys.exit('method not allowed')
