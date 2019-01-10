import os
import sys
import time
import socket
import socketserver
from hashlib import md5

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


date_log = '%Y%m%d%H%M%S'
usage_error = 'usage error: python3 server.py <file.xml>'
methods_allowed = 'invite', 'ack', 'bye'
att = {'account': ['username', 'passwd'],
       'uaserver': ['ip', 'puerto'],
       'rtpaudio': ['puerto'],
       'regproxy': ['ip', 'puerto'],
       'log': ['path'],
       'audio': ['path']}

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


class LOGGIN:

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
                    print('running: ' + cvlc + ' && ' + mp32rtp)
                    os.system(cvlc + ' && ' + mp32rtp)
                elif 'BYE' in data:
                    print('bye received')
                    self.wfile.write(bytes(sip_mess['200'], 'utf-8'))
            else:
                print('bad request')
                self.wfile.write(bytes(sip_mess['400'], 'utf-8'))


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
    log = LOGGIN(tags['log_path'])
    log.starting()
    if tags['uaserver_ip'] == '':
        ip = '127.0.0.1'
    else:
        ip = tags['uaserver_ip']
    port = int(tags['uaserver_puerto'])
    server_address = ip + ':' + str(port)
    server = socketserver.UDPServer((ip, port), SHandler)
    print('Listening at ' + server_address + '...\r\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.finishing()
