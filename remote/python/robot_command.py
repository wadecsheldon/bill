#!/usr/bin/env python
import socket
import pygame

def IntStr2Ints(strin):
    strout = ""
    for char in strin.split():
        strout = strout + chr(int(char))
    return strout
    

pygame.init()

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
    window = pygame.display.set_mode([150,150])
    print "sending to "+dest+" port "+str(destp)
    blarg = True
    arrows = [False,False,False,False]
    command = ""
    lastcommand = ""

    while blarg:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                blarg = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    arrows[0] = True
                elif event.key == pygame.K_DOWN:
                    arrows[1] = True
                elif event.key == pygame.K_LEFT:
                    arrows[2] = True
                elif event.key == pygame.K_RIGHT:
                    arrows[3] = True
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    arrows[0] = False
                elif event.key == pygame.K_DOWN:
                    arrows[1] = False
                elif event.key == pygame.K_LEFT:
                    arrows[2] = False
                elif event.key == pygame.K_RIGHT:
                    arrows[3] = False

        if arrows[3]:
            command = '127 137 0 127 255 255'
            
        if arrows[2]:
            command = '127 137 0 127 0 1'

        if arrows[1]:
            command = '127 137 255 129 127 255'

        if arrows[0]:
            command = '127 137 0 127 127 255'

        if True not in arrows:
            command = '127 137 0 0 0 0'
                
        if not pygame.key.get_focused():
            command = '127 137 0 0 0 0'
            arrows = [False,False,False,False]

        if command != lastcommand:
            silcox.sendto(IntStr2Ints(command),(dest, destp))
            lastcommand = command

    pygame.display.quit()
