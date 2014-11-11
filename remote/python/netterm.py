#!/usr/bin/env python
import socket

            #Initial setup type stuff
mode = raw_input("Direction (Send (default) or Receive): ").lower()
if mode not in ('send','receive'):
    print "Direction not recognized, defaulting to Send"
    mode = "send"
while True:
    host = raw_input("Host ip: ")
    if host != "":
            for part in host.split('.'):
                    if not part.isdigit():
                            print "Invalid IP. Please try again."
                            continue
                    if int(part) < 0 or int(part) > 255:
                            print "Invalid IP. Please try again."
                            continue
    break
while True:
    hostp = int(raw_input("Host port: "))
    if hostp >= 1 or hostp <= 65535:
        break
    print "Invalid port. Please try again."
if mode == "send":
    while True:
        dest = raw_input("Destination ip: ")
        for part in dest.split('.'):
            if not part.isdigit():
                print "Invalid IP. Please try again."
                continue
            if int(part) < 0 or int(part) > 255:
                print "Invalid IP. Please try again."
                continue
        break
    print dest
    while True:
        destp = int(raw_input("Destination port: "))
        if destp >= 1 or destp <= 65535:
            break
        print "Invalid port. Please try again."
prot = raw_input("Protocol (TCP (default) or UDP): ").lower()
if prot not in ('tcp','udp'):
    print "Protocol not recognized, defaulting to TCP"
    mode = "tcp"

if prot == "udp":   #figure out protocol to use, create socket
    typ = socket.SOCK_DGRAM
else:
    typ = socket.SOCK_STREAM
silcox = socket.socket(socket.AF_INET, typ)

if host == "":
    silcox.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

if mode == "receive":   #receive data
    silcox.bind((host, hostp))
    print "receiving on "+host+" port "+str(hostp)
    if prot == "tcp":
        silcox.listen(1)
        print "waiting for connection..."
        conn, addr = silcox.accept()
        print "connected to "+addr[0]
    else:
        conn = silcox
    while True:
        msg = conn.recv(1024)
        if msg != '':
            print msg
else:                   #otherwise send
    print "sending to "+dest+" port "+str(destp)
    while True:
        silcox.sendto(raw_input(),(dest, destp))

