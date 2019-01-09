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

def get_digest(nonce, passwd, encoding='utf-8'):
    digest = md5()
    digest.update(bytes(nonce, encoding))
    digest.update(bytes(passwd, encoding))
    digest.digest()

    return digest.hexdigest()


class XMLHandler(ContentHandler):

    def __init__(self, att_list):
        self.conf = {}
        self.att = att_list

    def startElement(self, name, attrs):
        if name in self.att:
            for att in self.att[name]:
                self.conf[name + "_" + att] = attrs.get(att, '')

    def get_tags(self):
        return self.conf


class LOG:

    def __init__(self, file_name):
        if not os.path.exists(file_name):
            os.system('touch ' + file_name)
        self.file = file_name

    def starting(self):
        now = time.gmtime(time.time() + 3600)
        log = open(self.file, 'a')
        log.write(time.strftime((date_log), now) + ' Starting...\n')
        log.close()

    def error(self, message):
        now = time.gmtime(time.time() + 3600)
        error_message = ' Error: ' + message + '\n'
        log = open(self.file, 'a')
        log.write(time.strftime((date_log), now) + error_message)
        log.close()

    def sent_to(self, address, message):
        line = ''
        for part in message.split('\r\n'):
            if part != '':
                line += part
            line += ' '
        line += '\n'
        now = time.gmtime(time.time() + 3600)
        sent_message = ' Sent to: ' + address + ': ' + line
        log = open(self.file, 'a')
        log.write(time.strftime((date_log), now) + sent_message)
        log.close()

    def received_from(self, address, message):
        line = ''
        for part in message.split('\r\n'):
            if part != '':
                line += part
            line += ' '
        line += '\n'
        now = time.gmtime(time.time() + 3600)
        received_message = ' Received from: ' + address + ' ' + line
        log = open(self.file, 'a')
        log.write(time.strftime((date_log), now) + received_message)
        log.close()

    def finishing(self):
        now = time.gmtime(time.time() + 3600)
        log = open(self.file, 'a')
        log.write(time.strftime((date_log), now) + ' Finishing\n')
        log.close()


class SIPHandler(socketserver.DatagramRequestHandler):
    reg = {}
    pwd = {}
    sesions = {}
    nonce = {}

    def json2register(self):
        try:
            with open(tags['database_path'], 'r') as jsonfile:
                self.reg = json.load(jsonfile)
        except:
            pass

    def json2passwd(self):
        try:
            with open(tags['database_passwdpath'], 'r') as jsonfile:
                self.pwd = json.load(jsonfile)
        except:
            pass

    def register2json(self):
        with open(tags['database_path'], 'w') as jsonfile:
            json.dump(self.reg, jsonfile, indent=3)

    def passwd2json(self):
        with open(tags['database_passwdpath'], 'w') as jsonfile:
            json.dump(self.pwd, jsonfile, indent=3)

    def expires_time(self):
        user_del = []
        now = time.gmtime(time.time() + 3600)
        try:
            for user in self.reg:
                if now >= time.strptime(self.reg[user]['expires'], date_reg):
                    user_del.append(user)
            for user in user_del:
                del self.reg[user]
        except:
            pass

    def sent_to(self, data, user_dst, port='', ip='127.0.0.1'):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            if port == '':
                port = self.reg[user_dst]['server_port']
            my_socket.connect((ip, int(port)))
            my_socket.send(bytes(data, 'utf-8'))
            log.sent_to(ip + ':' + port, data)

    def receive(self, data, user_dst, ip='127.0.0.1'):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            port = self.reg[user_dst]['server_port']
            my_socket.connect((ip, int(port)))
            my_socket.send(bytes(data, 'utf-8'))
            log.sent_to(ip + ':' + port, data)
            try:
                reply = my_socket.recv(1024).decode('utf-8')
            except:
                log.error('Connection refused')

            return reply

    def handle(self):
        self.json2register()
        self.json2passwd()
        self.expires_time()

        address = self.client_address[0] + ':' + str(self.client_address[1])
        data = self.rfile.read().decode('utf-8')
        log.received_from(address, data)

        if 'REGISTER' in data:
            user = data.split()[1].split(':')[1]
            if user in self.reg:
                option = data.split()[4].split('\r\n')[0]
                if option == 0:
                    del self.reg[user]
                    self.wfile.write(bytes(sip_mess['200'], 'utf-8'))
                    log.sent_to(address, sip_mess['200'])
                    print('user ' + user + ' log out')
                else:
                    expires = time.gmtime(time.time() + 3600 + int(option))
                    expires = time.strftime(date_reg, expires)
                    self.reg[user]['expires'] = expires
                    self.wfile.write(bytes(sip_mess['200'], 'utf-8'))
                    log.sent_to(address, sip_mess['200'])
                    print('user ' + user + ' log in')
            else:
                if user in self.pwd:
                    if 'response' in data:
                        option = data.split('\r\n')[1].split()[1]
                        expires = time.gmtime(time.time() + 3600 + int(option))
                        expires = time.strftime(date_reg, expires)
                        nonce = self.nonce[user]
                        passwd = self.pwd[user]['passwd']
                        response = get_digest(nonce, passwd)
                        rsp_src = data.split('\r\n')[2].split('"')[1]
                        if rsp_src == response:
                            del self.nonce[user]
                            server_port = data.split()[1].split(':')[-1]
                            user_dicc = {'server_port': server_port,
                                         'expires': expires}
                            self.reg[user] = user_dicc
                            self.wfile.write(bytes(sip_mess['200'], 'utf-8'))
                            log.sent_to(address, sip_mess['200'])
                            print('user ' + user + ' log in')
                    else:
                        nonce = str(random.randint(00000000000, 99999999999))
                        line = sip_mess['401'].split('\r\n\r\n')[0] + '\r\n'
                        line += 'WWW Auhenticate: Digest nonce="'
                        line += nonce + '"\r\n\r\n'
                        self.wfile.write(bytes(line, 'utf-8'))
                        log.sent_to(address, line)
                        self.nonce[user] = nonce
                        print('user ' + user + ' requires authorization')
                else:
                    self.wfile.write(bytes(sip_mess['404'], 'utf-8'))
                    log.sent_to(address, sip_mess['404'])
                    print('user ' + user + ' not found')
        elif 'INVITE' in data:
            sdp = data.split('\r\n\r\n')[1].split('\r\n')
            src = sdp[1].split()[0].split('=')[1]
            print(src)
            print(self.reg)
            if src in self.reg:
                dst = data.split()[1].split(':')[1]
                if dst in self.reg:
                    sesion = sdp[2].split('=')[1]
                    self.sesions[sesion] = [src, dst]
                    reply = self.receive(data, dst)
                    self.wfile.write(bytes(reply, 'utf-8'))
                    print(src + ' starting sesion: ' + sesion)
                else:
                    self.wfile.write(bytes(sip_mess['404'], 'utf-8'))
                    log.sent_to(address, sip_mess['404'])
                    print('user ' + dst + ' not found')
            else:
                self.wfile.write(bytes(sip_mess['404'], 'utf-8'))
                log.sent_to(address, sip_mess['404'])
                print('user ' + src + ' not found')
        elif 'BYE' in data:
            dst = data.split()[1].split(':')[1]
            if dst in self.reg:
                reply = self.receive(data, dst)
                self.wfile.write(bytes(reply, 'utf-8'))
                print('bye received')
                sesion_del = []
                for sesion in self.sesions:
                    if dst in self.sesions[sesion]:
                        sesion_del.append(sesion)
                for sesion in sesion_del:
                    del self.sesions[sesion]
            else:
                self.wfile.write(bytes(sip_mess['404'], 'utf-8'))
                log.sent_to(address, sip_mess['404'])
        elif 'ACK' in data:
            dst = data.split()[1].split(':')[1]
            if dst in self.reg:
                self.sent_to(data, dst)
            else:
                self.wfile.write(bytes(sip_mess['404'], 'utf-8'))
                log.sent_to(address, sip_mess['404'])
                print('user ' + dst + ' not found')
        else:
            if len(data.split()) >= 9:
                code = data.split()[7]
            else:
                code = data.split()[1]
            if code in sip_mess:
                if code == '200' and (len(data.split()) >= 9):
                    sdp = data.split('\r\n\r\n')[4]
                    sesion = sdp.split('\r\n')[2].split('=')[-1]
                    src = sdp.split('\r\n')[1].split()[0].split('=')[1]
                    if src == self.sesions[sesion][0]:
                        dst = self.sesions[sesion][1]
                    else:
                        dst = self.sesions[sesion][0]
                    reply = self.receive(data, dst)
                    self.wfile.write(bytes(reply, 'utf-8'))
                elif code == '200' and (len(data.split()) == 3):
                    port = str(self.client_address[1])
                    Bad = False
                    for user in self.reg:
                        if port == self.reg[user]['client_port']:
                            Bad = True
                    if not Bad:
                        for sesion in self.sesions:
                            if len(self.sesions[sesion]) == 1:
                                sesion_del.append(sesion)
                                dst = self.sesion[0]
                        del self.sesions[sesion]
                        port_dst = self.reg[dst]['client_port']
                        self.sent_to(data, dst, port_dst)

            else:
                self.wfile.write(bytes(sip_mess['405'], 'utf-8'))
                print('method not allowed')

        self.expires_time()
        self.passwd2json()
        self.register2json()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(usage_error)
    else:
        if os.path.exists(sys.argv[1]):
            xml_file = sys.argv[1]
        else:
            sys.exit('file ' + sys.argv[1] + ' not found')
    parser = make_parser()
    xml_list = XMLHandler(att)
    parser.setContentHandler(xml_list)
    parser.parse(open(xml_file))
    tags = xml_list.get_tags()
    log = LOG(tags['log_path'])
    pr_name = tags['server_name']
    if tags['server_ip'] == '':
        pr_ip = '127.0.0.1'
    else:
        pr_ip = tags['server_ip']
    pr_port = int(tags['server_puerto'])
    pr_address = pr_ip + ':' + str(pr_port)
    log.starting()
    proxy = socketserver.UDPServer((pr_ip, pr_port), SIPHandler)
    print('Server ' + pr_name + ' listening at ' + pr_address + '...\r\n')
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        print('\nEnd ' + pr_name)
    log.finishing()
