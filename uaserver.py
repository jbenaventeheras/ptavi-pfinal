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
class SHandler(socketserver.DatagramRequestHandler):
    rtp = []

    def send_proxy(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            ip = tags['regproxy_ip']
            port = tags['regproxy_puerto']
            my_socket.connect((ip, int(port)))
            my_socket.send(bytes(data, 'utf-8'))
            log.sent_to(ip + ':' + port, data)

    def handle(self):
        data = self.rfile.read().decode('utf-8')
        address = self.client_address[0] + ':' + str(self.client_address[1])
        log.received_from(address, data)
        if data != '':
            method = data.split()[0]
            if str.lower(method) in methods_allowed:
                if 'INVITE' in data:
                    sdp = data.split('\r\n\r\n')[1]
                    usr_dst = sdp.split('\r\n')[1]
                    usr_src = 'o=' + tags['account_username'] + ' '
                    usr_src += tags['uaserver_ip']
                    sdp = sdp.replace(usr_dst, usr_src)
                    rtp_dst = sdp.split('\r\n')[4]
                    self.rtp.append(usr_dst.split()[-1])
                    self.rtp.append(rtp_dst.split()[1])
                    rtp_src = 'm=audio ' + tags['rtpaudio_puerto'] + ' RTP'
                    sdp = sdp.replace(rtp_dst, rtp_src)
                    sdp = 'Content-Type: application/sdp\r\n\r\n' + sdp
                    dst = usr_dst.split()[0].split('=')[1]
                    print('invite received from ' + dst)
                    self.wfile.write(bytes(sip_mess['100'], 'utf-8'))
                    log.sent_to(server_address, sip_mess['100'])
                    self.wfile.write(bytes(sip_mess['180'], 'utf-8'))
                    log.sent_to(server_address, sip_mess['180'])
                    self.wfile.write(bytes(sip_mess['200'] + sdp, 'utf-8'))
                    log.sent_to(server_address, sip_mess['200'] + sdp)
                elif 'ACK' in data:
                    mp32rtp = './mp32rtp -i ' + self.rtp[0]
                    mp32rtp += ' -p ' + self.rtp[1]
                    mp32rtp += ' < ' + tags['audio_path']
                    cvlc = 'cvlc rtp://@' + self.rtp[0] + ':' + self.rtp[1]
                    #print('running: ' + mp32rtp)
                    #os.system(mp32rtp)
                    print('running: ' + cvlc + ' && ' + mp32rtp)
                    os.system(cvlc + ' && ' + mp32rtp)
                elif 'BYE' in data:
                    print('bye received')
                    self.wfile.write(bytes(sip_mess['200'], 'utf-8'))
            else:
                print('bad request')
                self.wfile.write(bytes(sip_mess['400'], 'utf-8'))
