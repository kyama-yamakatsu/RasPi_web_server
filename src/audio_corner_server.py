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
ADR_RELAY = 0b00000000
ADR_LED   = 0b00010000

dat_pin = 11
bck_pin = 13
wck_pin = 15
ind_pin = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(dat_pin,GPIO.OUT)
GPIO.setup(bck_pin,GPIO.OUT)
GPIO.setup(wck_pin,GPIO.OUT)
GPIO.setup(ind_pin,GPIO.OUT)

port = 2000
proc = None

# 明るさレベルは 0-255
lightL = '127'
lightD = '127'
lightA = '127'


# シリアル出力を行う
def serial_out( adr, data ):
    out = adr | data;
    i = 0
    GPIO.output(ind_pin,GPIO.HIGH)
    GPIO.output(wck_pin,GPIO.LOW)
    while i<8:
        GPIO.output(bck_pin,GPIO.LOW)
        sleep(1/1000)
        if out & 0x1:
#           print('1')
            GPIO.output(dat_pin,GPIO.HIGH)
        else:
#           print('0')
            GPIO.output(dat_pin,GPIO.LOW)
        out = out >> 1
        i = i+1
        sleep(1/1000)
        GPIO.output(bck_pin,GPIO.HIGH)
        sleep(1/1000)

    GPIO.output(wck_pin,GPIO.HIGH)
    GPIO.output(ind_pin,GPIO.LOW)


# 外部 Arduino Socket に接続し送信する
def socket_out( adr, data ):
    out_server = (adr, port)
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        out_socket.connect(out_server)
    except socket.error as e:
        print( "args:", e.args )
        out_socket.close()
        return;
    out_socket.send( ('light\n' + data).encode() )
    out_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('127.0.0.1', port))
# server_socket.bind((socket.gethostname(), port))
#   socket.gethostname() -> "raspberrypi"
server_socket.bind(('', port))
server_socket.listen(5)

while True:

    print('wait..')
    connection, address = server_socket.accept()
    recv = connection.recv(4096).decode()
    data = recv.splitlines()
    command = data[0]
    param = data[1]
    acPower =  data[2]
    spSwap =  data[3]
    sp2nd =  data[4]

    print('command=' + command)

    # 各状態に合せシリアルバイトデータを作成して出力
    if command == 'acPower':
        bits = 0b0;
        if ( acPower == '1' ):
            bits = 0b1
        if spSwap == '1':
            bits = bits | 0b10
        if sp2nd == '1':
            bits = bits | 0b100
        serial_out(ADR_RELAY, bits)

    elif command == 'spSwap':
        bits = 0b0
        if ( acPower == '1' ):
            bits = 0b1
        if spSwap == '1':
            bits = bits | 0b10
        if sp2nd == '1':
            bits = bits | 0b100
        serial_out(ADR_RELAY, bits)

    elif command == 'sp2nd':
        bits = 0b0
        if ( acPower == '1' ):
            bits = 0b1
        if spSwap == '1':
            bits = bits | 0b10
        if sp2nd == '1':
            bits = bits | 0b100
        serial_out(ADR_RELAY, bits)

    # 以下は command + param でコマンド発行が出来るタイプ
    elif command == 'light':
        ldata = int(param)
        ldata = (11-ldata)+4; # オペアンプの補正処理
        serial_out(ADR_LED, ldata)

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

    elif command == 'rLightL':
        lightL = lightM = lightH = '40'
        socket_out('192.168.1.7', lightL)
        socket_out('192.168.1.8', lightM)
        socket_out('192.168.1.9', lightH)
    elif command == 'rLightM':
        lightL = lightM = lightH = '127'
        socket_out('192.168.1.7', lightL)
        socket_out('192.168.1.8', lightM)
        socket_out('192.168.1.9', lightH)
    elif command == 'rLightH':
        lightL = lightM = lightH = '255'
        socket_out('192.168.1.7', lightL)
        socket_out('192.168.1.8', lightM)
        socket_out('192.168.1.9', lightH)
        
    # 以下は外部の Arduino Socket に向けてコマンド送信を行う
    # param が "start" の時は初期データのリクエスト
    elif command == 'lightL':
        if param != 'start':
            lightL = str(param)
        socket_out('192.168.1.7', lightL)
    elif command == 'lightD':
        if param != 'start':
            lightD = str(param)
        socket_out('192.168.1.8', lightD)
    elif command == 'lightA':
        if param != 'start':
            lightA = str(param)
        socket_out('192.168.1.9', lightA)


connection.close()
server_socket.close()
print('server close...')
exit(0)
