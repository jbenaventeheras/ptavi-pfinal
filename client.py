#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""
import socket
import sys

if len(sys.argv) != 3:
        sys.exit('Usage: python3 client.py method receiver@IP:SIPport')
else:
    try:
        method = str.upper(sys.argv[1])
        sip_name = sys.argv[2].split('@')[0]
        SERVER = sys.argv[2].split('@')[1].split(':')[0]
        PORT = int(sys.argv[2].split(':')[1])
    except:
        sys.exit('Usage: python3 client.py method receiver@IP:SIPport')

# Contenido que vamos a enviar
LINE = method + ' sip:' + sys.argv[2].split(':')[0] + ' SIP/2.0' + '\r\n\r\n'

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((SERVER, PORT))
    print('ENVIANDO... ' + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    server_OK = data.decode('utf-8').split(' ')[-1]
    print('RECIBIDO EN SOCKET MENSAJE: ' + data.decode('utf-8'))
    if server_OK == "OK":
        LINE = 'ACK sip:' + sys.argv[2].split(':')[0] + ' SIP/2.0' + '\r\n\r\n'

print("Fin.")
