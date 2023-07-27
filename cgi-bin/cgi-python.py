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
lightL = '50'
lightD = '50'
lightA = '50'

# ラスト状態を読み込む
fr = open('status.txt', 'r')
acPower = fr.readline().rstrip()
spSwap = fr.readline().rstrip()
sp2nd = fr.readline().rstrip()
volume = fr.readline().rstrip()
light = fr.readline().rstrip()
lightL = fr.readline().rstrip()
lightD = fr.readline().rstrip()
lightA = fr.readline().rstrip()
fr.close()

# index.htm からの引数を読む、常に command + param 形式
qh = cgi.FieldStorage(keep_blank_values=True)
command = qh.getfirst('command','')
param = qh.getfirst('param','')

# トグル状態の管理
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

# 状態の保存と変更
elif command == 'volume':
    volume = param
 
elif command == 'light':
    light = param

elif command == 'lightL':
    lightL = param
elif command == 'lightD':
    lightD = param
elif command == 'lightA':
    lightA = param


# おまじない
print('Content-Type: text/html\n')
# 最新状態を index.htm に返す
print(acPower)
print(spSwap)
print(sp2nd)
print(volume)
print(light)
print(lightL)
print(lightD)
print(lightA)

# 最新状態を保存する
# chmod 666 status.txt が必要
fw = open('status.txt', 'w')
fw.write(acPower + '\n')
fw.write(spSwap + '\n')
fw.write(sp2nd + '\n')
fw.write(volume + '\n')
fw.write(light + '\n')
fw.write(lightL + '\n')
fw.write(lightD + '\n')
fw.write(lightA + '\n')
fw.close()

# オーディオコーナー操作サーバーに依頼する
host = '127.0.0.1'
port = 2000
server = (host, port)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 本来 command + param だけで良さげだが、バイトデータを作るため
socket.connect(server)
socket.send((command+'\n'+param+'\n'+acPower+'\n'+spSwap+'\n'+sp2nd).encode())
socket.close()

exit(0)
