#!/usr/bin/python

import cv2
camnum = 1
while True:
    cam = cv2.VideoCapture(camnum)
    if cam.read()[0]: break
    if camnum < 0: raise Exception('No camera found')
    camnum -= 1
def getimg():
    return cam.read()[1]
img = getimg()
height, width, depth = img.shape

def dif(img): return cv2.absdiff(img, cv2.convertScaleAbs(base))

threshold = 30
def th(img): return cv2.threshold(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY),
                                  threshold, 255, cv2.THRESH_BINARY)[1]
minsize = 50
def blob(img):
    cnt = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    cnt = [c for c in cnt if cv2.contourArea(c) > minsize]
    return cnt

from subprocess import check_output, call
def rmold():
    for file in sorted(
        check_output(('find', '.', '-maxdepth', '1', '-type', 'f', '-name', '*.jpg', '-print0')).
        split((b'\x00'))
    )[1:-7]:
        call(('rm', file))

from time import time
def write(img):
    rmold()
    name = str(time()) + '.jpg'
    cv2.imwrite(name, cv2.flip(img, 1))
    return name

cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
def dispatch(cmd, args, img=None):
    if img is None: img = getimg()
    if('img' == cmd): return write(img)
    if('dif' == cmd): return write(dif(img))
    if('act' == cmd): return write(th(dif(img)))
    if('blob' == cmd):
        cnt = blob(th(dif(img)))
        cv2.drawContours(img, cnt, -1, (0, 255, 0), 3)
        return write(img)
    if('face' == cmd):
        s = ''
        for r in cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=4, minSize=(10,10), flags=cv2.CASCADE_DO_CANNY_PRUNING):
            cv2.rectangle(img, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (255, 0, 0))
            s += ' '.join([str(i) for i in r])
        return write(img) + ';' + s
    return 'Error: did not understand ' + cmd

from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
from json import dumps
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if '.jsonp' != url.path[-6:]: return SimpleHTTPRequestHandler.do_GET(self)
        query = parse_qs(url.query)
        try: callback = query['callback'][-1]
        except KeyError: raise Exception('No callback specified')
        data = dispatch(url.path[1:-6], query)
        self.send_response(200)
        self.send_header('Content-type', 'application/javascript')
        self.end_headers()
        self.wfile.write(callback + '(' + dumps(data) + ');')

from SocketServer import TCPServer
TCPServer.allow_reuse_address = True
TCPServer.timeout = 0.01
server = TCPServer(('', 8000), Handler)

import socket
insoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
insoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
insoc.settimeout(0.01)
insoc.bind(('', 3000))
insoc.listen(5)
outsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
outsoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
outsoc.settimeout(0.01)
buf = ''

import numpy as np
base = np.float32(img)

from select import select
try:
    while True:
        img = getimg()
        cv2.imwrite('tmp.jpg', img)
        call(('mv', 'tmp.jpg', 'cur.jpg'))

        cv2.accumulateWeighted(img, base, 0.1)

        server.handle_request()

        try: inp, addr = insoc.accept()
        except socket.error: pass
        try: inp
        except NameError: continue
        try:
            if len(select([inp], [], [], 0.01)[0]) > 0:
                data = inp.recv(1024)
                if len(data) > 0:
                    buf += data.replace("\n", '');
                    if ';' in buf:
                        try: outsoc.connect((addr[0], 3001))
                        except socket.error: pass

                        buf = buf.split(';', 1)
                        command = buf[0].split(' ')
                        buf = buf[1]
                        try: outsoc.sendall(dispatch(command[0], command[1:], img).replace(';', ' ') + ';')
                        except socket.error: pass

        except socket.error: continue

except:
    server.server_close()
    insoc.close()
    outsoc.close()
    cam.release()

    from sys import exc_info, exit
    if 'KeyboardInterrupt' != exc_info()[0].__name__: raise
    else: exit(0)
