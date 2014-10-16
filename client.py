#!/usr/bin/env python

import socket
import time
import getpass

host = '127.0.0.1'
port = 6679
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

while 1:
    name = raw_input('UserName:').strip()
    s.sendall(name)
    name_res = s.recv(1024)
    if name_res != 'OK':
        print '\033[31minvalid UserName\033[0m'
        continue
    passwd = getpass.getpass()
    s.sendall(passwd)
    pass_res = s.recv(1024)
    if pass_res != 'OK':
        print '\033[31mPassword Wrong\033[0m'
        continue
    break

print '\033[32mwelcome to ftp server, %s\033[0m' % name

while 1:
    cmd = raw_input('ftp >').strip()
    s.sendall(cmd)
    if not cmd:
        continue
    elif cmd == 'q':
        break
    elif cmd.split()[0] == 'get':
        status = s.recv(4096)
        if status == 'file not exists or is a directory' or status == 'Usage: get file_name':
            print status
            continue
        data = s.recv(4096)

        filename = cmd.split()[1]
        fd = file(filename,'wb')
        if data != 'empty':
            fd.write(data)
        fd.close()
    elif cmd.split()[0] == 'send':
        filename = cmd.split()[1]
        fd = file(filename, 'rb')
        data = fd.read()
        s.sendall(data)
        fd.close()
        time.sleep(0.5)
        s.sendall('file_send_done')
        data = s.recv(1024)
        print data
    elif cmd.split()[0] == 'cd':
        path = cmd.split()[1]
        data = s.recv(4096)
        if data != 'OK':
            print data
    else:
        data = s.recv(4096)
        print data

s.close()
