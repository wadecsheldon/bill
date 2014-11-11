#!/usr/bin/env python

def word2ints(word):
    ints = ""
    ints = str(word // 256) + " " + str(word % 256)
    return ints

import socket
import pygame
import math

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
    axes = [0,0]
    command = ""
    radius = 0
    speed = 0

    pygame.joystick.init()
    clock = pygame.time.Clock()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    while blarg:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                blarg = False

        axes[0] = joystick.get_axis(0)
        axes[1] = joystick.get_axis(1)

        theta = math.degrees(math.atan2(-(axes[1]),axes[0]))
        dist = math.sqrt(math.pow(axes[0],2) + math.pow(axes[1],2))

        speed = dist * 200
        if theta < 0:
            speed = 65536 - speed

        abstheta = abs(theta)

        if abstheta > 165:
            radius = 1
        elif abstheta < 95 and abstheta > 85:
            radius = 32768
        elif abstheta < 15:
            radius = 65535
        elif abstheta >= 15 and abstheta <= 85:
            radius = 65536 - (2000 * ((abstheta-15)/70))
        elif abstheta >= 95 and abstheta <= 165:
            radius = 2000 * (1-(abstheta-95)/70)

        if dist > .25:
            command = '127 137 ' + word2ints(int(speed)) + " " + word2ints(int(radius))
        else:
            command = '127 137 0 0 0 0'
                
        if not pygame.key.get_focused():
            command = '127 137 0 0 0 0'

        print command

        silcox.sendto(IntStr2Ints(command),(dest, destp))

        clock.tick(5)

    pygame.display.quit()
