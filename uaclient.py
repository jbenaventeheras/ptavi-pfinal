#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase SIPMessages y principal del client."""
import os
import sys
import time
import socket

from xml.sax import make_parser
from uaserver import XMLHandler, LOGGIN, get_digest

usage_error = 'usage error: python3 client.py <file.xml> <method> <option>'
methods_allowed = 'register, invite, bye, ack'
att = {'account': ['username', 'passwd'],
       'uaserver': ['ip', 'puerto'],
       'rtpaudio': ['puerto'],
       'regproxy': ['ip', 'puerto'],
       'log': ['path'],
       'audio': ['path']}


class SIPMessages:
    """Clase SIPMessages."""

    def __init__(self, user, port, ip, rtp_port):
        """Inicia user ip port rtp_port."""
        self.src = {'user': user, 'ip': ip, 'port': port, 'rtp_port': rtp_port}

    def register(self, option):
        """retorna linea con SIP de register."""
        line = 'REGISTER sip:' + self.src['user'] + ':' + self.src['port']
        line += ' SIP/2.0\r\nExpires: ' + option + '\r\n'

        return line

    def invite(self, option):
        """retorna linea con SIP de INVITE."""
        line = 'INVITE sip:' + option + ' SIP/2.0\r\n'
        line += 'Content-Type: application/sdp\r\n\r\nv=0\r\n'
        line += 'o=' + self.src['user'] + ' ' + self.src['ip'] + '\r\n'
        line += 's=Super-Sesion\r\nt=0\r\n'
        line += 'm=audio ' + self.src['rtp_port'] + ' RTP\r\n'

        return line

    def get_mess(self, method, option):
        """retorna el mensaje ya formado que se eligio del terminal."""
        if str.lower(method) == 'register':
            return self.register(option)
        elif str.lower(method) == 'invite':
            return self.invite(option)
        elif str.lower(method) == 'bye':
            return 'BYE sip:' + option + ' SIP/2.0\r\n'
        elif str.lower(method) == 'ack':
            return 'ACK sip:' + option + ' SIP/2.0\r\n'


if __name__ == '__main__':

    if len(sys.argv) != 4:
        sys.exit(usage_error)
    else:
        if os.path.exists(sys.argv[1]):
            xml_file = sys.argv[1]
            method = sys.argv[2]
            option = sys.argv[3]
        else:
            sys.exit('file ' + sys.argv[1] + ' not found')
    parser = make_parser()
    xml_list = XMLHandler(att)
    parser.setContentHandler(xml_list)
    parser.parse(open(xml_file))
    tags = xml_list.get_tags()
    log = LOGGIN(tags['log_path'])
    user = tags['account_username']
    psswd = tags['account_passwd']
    port = tags['uaserver_puerto']
    ip = tags['uaserver_ip']
    user_address = user + ':' + port
    rtp_port = tags['rtpaudio_puerto']
    pr_ip = tags['regproxy_ip']
    pr_port = tags['regproxy_puerto']
    pr_address = pr_ip + ':' + pr_port
    sip_mess = SIPMessages(user, port, ip, rtp_port)
    log.starting()

    if str.lower(method) in methods_allowed:
        line = sip_mess.get_mess(str.lower(method), option) + '\r\n'

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((pr_ip, int(pr_port)))
            my_socket.send(bytes(line, 'utf-8'))

            log.sent_to(pr_address, line)

            try:
                data = my_socket.recv(1024).decode('utf-8')
                log.received_from(pr_address, data)
            except:
                log.error('Connection refused')
                sys.exit('connection refused')

            if '100' in data:
                print('trying received')
                if '180' in data:
                    print('ringing received')
                    if '200' in data:
                        print('ok received')
                        sdp = data.split('\r\n\r\n')[4]
                        ip = sdp.split('\r\n')[1].split()[-1]
                        port = sdp.split('\r\n')[4].split()[1]
                        mp32rtp = './mp32rtp -i ' + ip + ' -p ' + port
                        mp32rtp += ' < ' + tags['audio_path']
                        line = sip_mess.get_mess('ack', option) + '\r\n'
                        cvlc = 'cvlc rtp://@' + ip + ':' + port
                        my_socket.send(bytes(line, 'utf-8'))
                        log.sent_to(pr_address, line)
                        print('running: ' + cvlc + ' && ' + mp32rtp)
                        os.system(cvlc + ' && ' + mp32rtp)
            elif '200' in data:
                print('ok received')
            elif '400' in data:
                print('bad request received')
            elif '401' in data:
                print('authorized required')
                nonce = data.split('"')[1]
                response = get_digest(nonce, psswd)
                auth = 'Authorization: Digest response="' + response + '"'
                line = sip_mess.get_mess(str.lower(method), option)
                line += auth + '\r\n\r\n'
                my_socket.send(bytes(line, 'utf-8'))

                log.sent_to(pr_address, line)

                try:
                    data = my_socket.recv(1024).decode('utf-8')
                except:
                    log.error('Connection refused')
                    sys.exit('connection refused')

                log.received_from(pr_address, data)

                if '200' in data:
                    print('ok received')
                else:
                    print(data)

            elif '404' in data:
                print('user not found')
            elif '405' in data:
                print('method not allowed')

    else:
        log.error('Method not allowed')
        sys.exit('method not allowed')

    log.finishing()
