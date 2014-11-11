#!/usr/bin/env python

def word2Ints(word):
    ints = ""
    ints = str(word // 256) + " " + str(word % 256)
    return ints

def lights2Comm(lightsList):
    mono = 0
    if lightsList[2]:
        mono += 2
    if lightsList[3]:
        mono += 8
    return "127 139 " + str(mono) + " " + str(lightsList[0]) + " " + str(lightsList[1])

import socket
import pygame
import math
import time

def intStr2Ints(strin):
    strout = ""
    for char in strin.split():
        strout = strout + chr(int(char))
    return strout
    

pygame.init()

dev = False
destp = 0
dest = "null"

            #Initial setup type stuff
mode = raw_input("Direction (Send (default) or Receive): ").lower()
if mode != "dev":
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

else:
    dev = True

    

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
    axes = []
    command = ""
    commandlist = [""]
    lights = [0,255,False,False]
    radius = 0
    speed = 0
    cruise = False
    cruise_speed = -300
    spin = False

    pygame.joystick.init()
    clock = pygame.time.Clock()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    axes = [0] * joystick.get_numaxes()


    commandlist.append(lights2Comm(lights))
    commandlist.append('127 140 0 1 72 16')

    if not dev:         #send initial command list
        for strin in commandlist:
            if strin != "":
                silcox.sendto(intStr2Ints(strin),(dest, destp))
                time.sleep(0.1)

    while blarg:
        commandlist = [""]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                blarg = False

            if event.type == pygame.JOYBUTTONDOWN:
                button = event.dict["button"]

                if button == 8:
                    cruise = not cruise
                    if cruise:
                        cruise_speed = speed
                        lights[3] = True
                        commandlist.append(lights2Comm(lights))
                    else:
                        cruise_speed = -300
                        lights[3] = False
                        commandlist.append(lights2Comm(lights))
                elif button == 2:
                    spin = True
                elif button == 4:
                    commandlist.append('127 141 0')

            if event.type == pygame.JOYBUTTONUP:
                button = event.dict["button"]

                if button == 2:
                    spin = False

        for axis in range(joystick.get_numaxes()):
            axes[axis] = joystick.get_axis(axis)
            
        speed = max(-(axes[2] * 200),cruise_speed)

        if speed < 0:
            speed = 65536 + speed

        if spin:
            if axes[0] >= 0.15:
                radius = 65535
            elif axes[0] <= -0.15:
                radius = 1
            else:
                radius = 32768
        else:
            if axes[0] < 0.15 and axes[0] > -0.15:
                radius = 32768
            elif axes[0] >= 0.15:
                radius = 65536 - (2000 * (1 - (axes[0] - 0.15) / 0.85))
                radius = min(radius, 65435)
            elif axes[0] <= -0.15:
                radius = 2000 * (1 - (axes[0] + 0.15) / -0.85)
                radius = max(radius, 100)

        if speed > 0.01 or speed < -0.01:
            command = '127 137 ' + word2Ints(int(speed)) + " " + word2Ints(int(radius))
        else:
            command = '127 137 0 0 0 0'
                
        if not pygame.key.get_focused():
            command = '127 137 0 0 0 0'

        commandlist[0] = command

        print command

        if not dev:
            for strin in commandlist:
                if strin != "":
                    silcox.sendto(intStr2Ints(strin),(dest, destp))
                    time.sleep(0.1)
                    

        clock.tick(5)

    if not dev:
        silcox.sendto(intStr2Ints('127 137 0 0 0 0'),(dest, destp))
        time.sleep(0.1)
        silcox.sendto(intStr2Ints(lights2Comm([255,255,False,False])),(dest, destp))
    pygame.display.quit()
