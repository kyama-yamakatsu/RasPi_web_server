#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 起動 $ ./audio_corner_server.py &
# 停止 $ kill pid
#
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep


# Address define
ADR_POWER_RELAY =  0b00010000
ADR_SPEAKER =  0b00100000
ADR_LED = 0b01000000

dat_pin = 11
bck_pin = 13
wck_pin = 13 # 15 !!!
ind_pin = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(dat_pin,GPIO.OUT)
GPIO.setup(bck_pin,GPIO.OUT)
GPIO.setup(wck_pin,GPIO.OUT)
GPIO.setup(ind_pin,GPIO.OUT)
GPIO.setup(15,GPIO.OUT) # !!!


host = '127.0.0.1'
port = 2000
server = (host, port)

proc = None

def serial_out( adr, data):
    #adr = adr << 4
    out = adr | data;
    i = 0
    GPIO.output(ind_pin,GPIO.HIGH)
    GPIO.output(wck_pin,GPIO.LOW)
    while i<8:
        GPIO.output(bck_pin,GPIO.LOW)
        sleep(1/1000)
        if out & 0x1:
            print('1')
            GPIO.output(dat_pin,GPIO.HIGH)
        else:
            print('0')
            GPIO.output(dat_pin,GPIO.LOW)
        out = out >> 1
        i = i+1
        sleep(1/1000)
        GPIO.output(bck_pin,GPIO.HIGH)
        sleep(1/1000)

    GPIO.output(wck_pin,GPIO.HIGH)
    GPIO.output(ind_pin,GPIO.LOW)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host, port))
socket.listen(5)

while True:

    print('wait..')
    connection, address = socket.accept()
    recv = connection.recv(4096).decode()
    data = recv.splitlines()
    command = data[0]
    param = data[1]
    acPower =  data[2]
    spSwap =  data[3]
    sp2nd =  data[4]

    print('command=' + command)

    # 状態の変更
    if command == 'acPower':
        data = 0b0;
        if ( acPower == '1' ):
            data = 0b1
        serial_out(ADR_POWER_RELAY, data)

    elif command == 'spSwap':
        data = 0x0
        if spSwap == '1':
            data = 0x1
            GPIO.output(15,GPIO.HIGH) # !!!
        else: #!!!
            GPIO.output(15,GPIO.LOW) # !!!
        serial_out(ADR_SPEAKER, data)

    elif command == 'sp2nd':
        print('not yet ' + sp2nd)

    elif command == 'light':
        serial_out(ADR_LED, int(param))

    elif command == 'volume':
        subprocess.run("amixer -c 1 -D pulse set Master "+param+"%", shell=True, stdout=subprocess.PIPE)

    elif command == 'irStop':
        if proc != None:
            #proc.terminate()
            #proc.kill()
            #proc.wait()
            subprocess.run("killall mplayer", shell=True)
            proc = None

    elif command == 'irStation':
        if proc != None:
            subprocess.run("killall mplayer", shell=True)
        proc=subprocess.Popen("mplayer "+param, shell=True)
        #proc=subprocess.Popen("mplayer "+param, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

connection.close()
socket.close()
print('server close...')
exit(0)
