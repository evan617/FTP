#!/usr/bin/env python
#coding=utf-8

import socket
import os
import SocketServer

HOST = '0.0.0.0'
PORT = 6679
BUFFERSIZE = 4096
auth_dic={'ftp':'ftp', 'evan':'evan'}

class MyFTPRequestHandler(SocketServer.StreamRequestHandler):
    '''ftp server, the default path is at /var/ftp/, make sure that you already
    have the dir and have the access to it before you start the server'''

    def handle(self):
        self.path = '/var/ftp/'
        self.auth()
        os.chdir(self.path)
        self.run()

    def auth(self):
        while True:
            self.name = self.request.recv(BUFFERSIZE)
            if self.name not in auth_dic:
                self.request.sendall('FAILD')
                continue
            else:
                self.request.sendall('OK')
            self.passwd = self.request.recv(BUFFERSIZE)
            if self.passwd != auth_dic[self.name]:
                self.request.sendall('FAILED')
                continue
            else:
                self.request.sendall('OK')
            self.type = 0 if self.name == 'ftp' else 1
            break

    def getfile(self, filename):
        try:
            ##f_name = self.path + filename
            fd = file(filename,'rb')
            self.request.sendall('OK')
        except IndexError:
            self.request.sendall('Usage: get file_name')
        except IOError:
            self.request.sendall('file not exists or is a directory')
        else:
            while 1:
                filedata = fd.read(BUFFERSIZE)
                if not filedata:break
                self.request.sendall(filedata)
            print 'send %s to server %s' % (filename, self.client_address)


    def sendfile(self, filename):
        ##f_name = self.path + filename
        fd = file(filename,'wb')
        while True:
            data2 = self.request.recv(BUFFERSIZE)
            if data2 == 'file_send_done':
                break
            fd.write(data2)
        fd.close()
        print 'receive %s' % filename
        response = '0K'
        self.request.sendall(response)

    def cdpath(self, pathname):
        if not os.path.isdir(pathname):
            self.request.sendall('%s not exist or is not a directory' % pathname)
        else:
            self.request.sendall('OK')
            os.chdir(pathname)

    def run(self):
        while True:
            data = self.request.recv(BUFFERSIZE).strip()
            print 'receive from %s : %s' % (self.client_address, data)
            if data == '?' or data == 'help':
                response = '\033[31;1mls\t\t\tshow the current directory\nget file\t\tget the file from ftp server\nsend file\t\tsend the file to ftp server\033[0m'
                self.request.sendall(response)
            elif data == 'q':
                break
            elif data == 'ls':

                response = os.popen(data).read()
                self.request.sendall(response)
            elif data.split()[0] == 'get':  #需要完善
                self.getfile(data.split()[1])
            elif data.split()[0] == 'send':
                self.sendfile(data.split()[1])
            elif data.split()[0] == 'cd':
                self.cdpath(data.split()[1])
            else:
                response = 'invalid command, see help'
                self.request.sendall(response)

    def finish(self):
        return SocketServer.BaseRequestHandler.finish(self)



if __name__ == '__main__':
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyFTPRequestHandler)
    server.serve_forever()