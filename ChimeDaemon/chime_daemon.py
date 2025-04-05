#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import threading
import time
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject


class SignalEmitter(QObject):
    show_popup = pyqtSignal(str)


class PopupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ウィンドウの設定
        self.setWindowTitle("チャイム通知")
        self.setGeometry(100, 100, 600, 250)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 中央に配置するウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # レイアウト
        layout = QVBoxLayout(central_widget)
        
        # メッセージラベル
        self.message_label = QLabel("メッセージを受信しました")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(self.message_label)
        
        # ウィンドウのスタイル設定
        self.setStyleSheet("background-color: rgba(0, 0, 150, 200);")
        
        # 自動で消えるタイマー
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)
        
    def show_message(self, message):
        # 画面の中央に表示
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                 int((screen.height() - size.height()) / 2))
        
        # メッセージを設定
        if message:
            self.message_label.setText(message)
        else:
            self.message_label.setText("メッセージを受信しました")
        
        # 表示して、5秒後に消える
        self.show()
        self.timer.start(5000)  # 5秒


class ChimeDaemon:
    def __init__(self, host='0.0.0.0', port=9358, sound_file=None):
        self.host = host
        self.port = port
        
        # サウンドファイルの設定
        if sound_file and os.path.exists(sound_file):
            self.sound_file = sound_file
        else:
            # デフォルトのサウンドファイル（macOSのシステム音）
            self.sound_file = "/System/Library/Sounds/Ping.aiff"
        
        # UDPソケットの初期化
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # ブロードキャスト受信の設定
        self.socket.bind((self.host, self.port))
        
        # QTアプリケーション
        self.app = QApplication(sys.argv)
        self.popup = PopupWindow()
        
        # シグナルエミッター（スレッド間通信用）
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.show_popup.connect(self.popup.show_message)
    
    def play_sound(self):
        """チャイム音を鳴らす（AppleScriptを使用）"""
        try:
            # AppleScriptを使用して現在のボリュームを取得して保存
            get_volume_cmd = "osascript -e 'output volume of (get volume settings)'"
            original_volume = subprocess.check_output(get_volume_cmd, shell=True).decode().strip()
            print(f"現在のボリューム: {original_volume}")
            
            # 5秒間繰り返し再生
            start_time = time.time()
            end_time = start_time + 5  # 5秒間再生
            
            # ボリュームを一時的に最大に設定 (100%)
            set_volume_cmd = "osascript -e 'set volume output volume 100'"
            subprocess.call(set_volume_cmd, shell=True)
            print("ボリュームを最大に設定しました")
            
            try:
                while time.time() < end_time:
                    # 音を再生 (afplayを使用)
                    subprocess.Popen(['afplay', self.sound_file])
                    time.sleep(0.5)
            finally:
                # 元のボリュームに戻す
                restore_volume_cmd = f"osascript -e 'set volume output volume {original_volume}'"
                subprocess.call(restore_volume_cmd, shell=True)
                print(f"ボリュームを元の設定 ({original_volume}) に戻しました")
        except Exception as e:
            print(f"サウンド再生エラー: {e}")
    
    def handle_message(self, message):
        """受信したメッセージを処理"""
        # サウンドを別スレッドで再生
        sound_thread = threading.Thread(target=self.play_sound)
        sound_thread.daemon = True
        sound_thread.start()
        
        # ポップアップ表示（QTメインスレッドで実行するため、シグナルを発行）
        try:
            decoded_message = message.decode('utf-8')
        except:
            decoded_message = "メッセージを受信しました"
        
        self.signal_emitter.show_popup.emit(decoded_message)
    
    def receive_loop(self):
        """UDP受信ループ"""
        print(f"UDPポート {self.port} で受信待機中...")
        
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                print(f"メッセージ受信: {addr} から {data}")
                self.handle_message(data)
            except Exception as e:
                print(f"受信エラー: {e}")
    
    def run(self):
        """デーモンの実行"""
        # 受信スレッドの開始
        receiver = threading.Thread(target=self.receive_loop)
        receiver.daemon = True
        receiver.start()
        
        # QTイベントループの開始
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    print("チャイムデーモンを起動します...")
    
    # コマンドライン引数からポート番号とサウンドファイルを取得（オプション）
    port = 9358  # デフォルトポート
    sound_file = None
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"無効なポート番号です: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        sound_file = sys.argv[2]
        if not os.path.exists(sound_file):
            print(f"サウンドファイルが見つかりません: {sound_file}")
            sound_file = None
    
    # デーモンの起動
    daemon = ChimeDaemon(port=port, sound_file=sound_file)
    daemon.run() 