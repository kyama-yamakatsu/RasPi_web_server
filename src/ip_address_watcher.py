#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 準備
# ~/.bashrc に以下の環境変数を記述しておく
#
# export GMAIL_ADDRESS="your_email_address"
# export GMAIL_APP_PASSWORD="your_app_password"
#
# 起動 $ ./ip_address_watcher.py &
# 停止 $ kill pid
#
import os
import time
import threading
import socket
import smtplib
from email.mime.text import MIMEText

ip_address = '0.0.0.0'


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_adr = s.getsockname()[0]
        s.close()
        return ip_adr
    except Exception as e:
        return f"Error: {e}"

def send_link_address(adr):
    sender_email = recipient_email = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    # MIMEText オブジェクト作成
    body = f"http://{adr}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Raspi IP address has changed"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)

        print("\nmail send..")

    except Exception as e:
        print(f"\nsend error..{e}")

def watcher():
    global ip_address
    if ip_address != get_ip_address():
        ip_address = get_ip_address()
        print(f"IP address has changed: {ip_address}")
        send_link_address(ip_address)

def run_scheduler():
    while True:
        watcher()
        # 3600秒 = 1時間 待機
        time.sleep(3600)


# main
# スレッドを作成し、実行を開始
# メインスレッドが終了したら、このスレッドも終了する設定
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
print("\nrunning..")

# メインスレッドはピーマン
try:
    while True:
        time.sleep(60)

except KeyboardInterrupt:
    print("\nending..")
