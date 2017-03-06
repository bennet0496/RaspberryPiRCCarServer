#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
from config import *
import socket, sys

GPIO.setmode(GPIO.BOARD)

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)

GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)

m1a = GPIO.PWM(Motor1A, 100)
m1b = GPIO.PWM(Motor1B, 100)
m1a.start(0)
m1b.start(0)

#m2a = GPIO.PWM(Motor2A, 100)
#m2b = GPIO.PWM(Motor2B, 100)
#m2a.start(0)
#m2b.start(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', TCPPORT))
sock.listen(1)
try:
    while True:
        print >> sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        try:
            print >> sys.stderr, 'connection from', client_address
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >> sys.stderr, 'received "%s"' % data
                if data:
                    print >> sys.stderr, 'Setting Motors...'
                    v1 = int(str(data).split(";")[0])
                    v2 = int(str(data).split(";")[1])
                    if v1 >= 0:
                        GPIO.output(Motor1E, GPIO.HIGH)
                        m1a.ChangeDutyCycle(0)
                        m1b.ChangeDutyCycle(v1)
                    else:
                        GPIO.output(Motor1E, GPIO.HIGH)
                        m1a.ChangeDutyCycle(v1 * -1)
                        m1b.ChangeDutyCycle(0)

                    if v2 < 0:
                        GPIO.output(Motor2E, GPIO.HIGH)
                        GPIO.output(Motor2A, GPIO.LOW)
                        GPIO.output(Motor2B, GPIO.HIGH)
                        #m2a.ChangeDutyCycle(0)
                        #m2b.ChangeDutyCycle(v2)
                    elif v2 > 0:
                        GPIO.output(Motor2E, GPIO.HIGH)
                        GPIO.output(Motor2A, GPIO.HIGH)
                        GPIO.output(Motor2B, GPIO.LOW)
                        #m2a.ChangeDutyCycle(v2 * -1)
                        #m2b.ChangeDutyCycle(0)
                    else:
                        GPIO.output(Motor2E, GPIO.LOW)
                        GPIO.output(Motor2A, GPIO.LOW)
                        GPIO.output(Motor2B, GPIO.LOW)
                        #connection.sendall(data)
                else:
                    print >> sys.stderr, 'no more data from', client_address
                    break
        finally:
            # Clean up the connection
            connection.close()
except KeyboardInterrupt:
    connection.close()
    GPIO.output(Motor1A, GPIO.LOW)
    GPIO.output(Motor1B, GPIO.LOW)
    GPIO.output(Motor2A, GPIO.LOW)
    GPIO.output(Motor2B, GPIO.LOW)

    GPIO.output(Motor1E, GPIO.LOW)
    GPIO.output(Motor2E, GPIO.LOW)
    GPIO.cleanup()
    print "Bye"