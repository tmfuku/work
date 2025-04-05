#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys

def send_udp_message(message, host="127.0.0.1", port=5000):
    """UDPメッセージを送信する"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message.encode('utf-8'), (host, port))
        print(f"メッセージを送信しました: {message}")
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # デフォルト値
    host = "127.0.0.1"
    port = 5000
    message = "テストメッセージ"
    
    # コマンドライン引数の処理
    if len(sys.argv) > 1:
        message = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"無効なポート番号です: {sys.argv[2]}")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        host = sys.argv[3]
    
    # UDPメッセージの送信
    send_udp_message(message, host, port) 