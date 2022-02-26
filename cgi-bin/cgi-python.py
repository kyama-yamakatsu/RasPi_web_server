#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import cgi
import socket

# default 状態
acPower = '0'
spSwap = '0'
sp2nd = '0'
volume = '50'
light = '8'

fr = open('status.txt')
acPower = fr.readline().rstrip()
spSwap = fr.readline().rstrip()
sp2nd = fr.readline().rstrip()
volume = fr.readline().rstrip()
light = fr.readline().rstrip()
fr.close()

# 引数を読む
qh = cgi.FieldStorage(keep_blank_values=True)
command = qh.getfirst('command','')
param = qh.getfirst('param','')

# 状態の変更
if command == 'acPower':
    if acPower == '0':
        acPower = '1'
    else:
        acPower = '0'
    spSwap = '0'
    sp2nd = '0'

elif command == 'spSwap':
    if spSwap == '0':
        spSwap = '1'
    else:
        spSwap = '0'

elif command == 'sp2nd':
    if sp2nd == '0':
        sp2nd = '1'
    else:
        sp2nd = '0'

elif command == 'volume':
    volume = param
 
elif command == 'light':
    light = param


# おまじない
print('Content-Type: text/html\n')
# 最新状態を返す
print(acPower)
print(spSwap)
print(sp2nd)
print(volume)
print(light)

# 最新状態を保存する
fw = open('status.txt', 'w')
fw.write(acPower + '\n')
fw.write(spSwap + '\n')
fw.write(sp2nd + '\n')
fw.write(volume + '\n')
fw.write(light + '\n')
fw.close()

# オーディオコーナー操作サーバーに依頼する
host = '127.0.0.1'
port = 2000
server = (host, port)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket.connect(server)
socket.send((command+'\n'+param+'\n'+acPower+'\n'+spSwap+'\n'+sp2nd).encode())
socket.close()

exit(0)
