#!/usr/bin/env python

import socket
import time
import getpass

host = '127.0.0.1'
port = 6679
BUFFERSIZE = 4096
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

while 1:
    name = raw_input('UserName:').strip()
    s.sendall(name)
    name_res = s.recv(BUFFERSIZE)
    if name_res != 'OK':
        print '\033[31minvalid UserName\033[0m'
        continue
    passwd = getpass.getpass()
    s.sendall(passwd)
    pass_res = s.recv(BUFFERSIZE)
    if pass_res != 'OK':
        print '\033[31mPassword Wrong\033[0m'
        continue
    break

print '\033[32mwelcome to ftp server, %s\033[0m' % name

while 1:
    cmd = raw_input('ftp >').strip()
    if not cmd:
        continue
    elif cmd == 'q':
        s.sendall(cmd)
        break
    elif cmd.split()[0] == 'get':
        s.sendall(cmd)
        status = s.recv(BUFFERSIZE)
        if status == 'file not exists or is a directory' or status == 'Usage: get file_name':
            print status
            continue
        filename = cmd.split()[1]
        fd = file(filename,'wb')
        while 1:
            filedata = s.recv(BUFFERSIZE)
            if not filedata:
                break
            fd.write(filedata)
            if len(filedata) < BUFFERSIZE:
                break
        fd.close()
    elif cmd.split()[0] == 'send':
        filename = cmd.split()[1]
        if not filename:
            print 'Usage: send filename'
            continue
        try:
            fd = file(filename, 'rb')
        except IOError:
            print '%s not exists or is a directory' % filename
            continue
        else:
            s.sendall(cmd)
        while 1:
            filedata = fd.read(BUFFERSIZE)
            if not filedata:
                break
            s.sendall(filedata)
        fd.close()
        time.sleep(0.5)
        s.sendall('file_send_done')
        data = s.recv(1024)
        print data
    elif cmd.split()[0] == 'cd':
        path = cmd.split()[1]
        data = s.recv(BUFFERSIZE)
        if data != 'OK':
            print data
    else:
        data = s.recv(BUFFERSIZE)
        print data

s.close()
