# チャイムデーモン

macOSで動作するUDP受信監視チャイムプログラムです。UDPメッセージを受信すると、チャイム音を鳴らし、画面にポップアップ通知を表示します。

## 必要条件

- Python 3.6以上
- PyQt5
- macOS（AppleScriptを使用するため）

## インストール

必要なライブラリをインストールします：

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使い方

デフォルト設定（ポート5000）で起動：

```bash
python chime_daemon.py
```

### カスタム設定

ポートを指定して起動：

```bash
python chime_daemon.py 8080
```

ポートとカスタムサウンドファイルを指定して起動：

```bash
python chime_daemon.py 8080 /path/to/your/sound.aiff
```

## UDP メッセージの送信方法

以下のような方法でUDPメッセージを送信できます：

### Pythonの例

```python
import socket

UDP_IP = "127.0.0.1"  # ローカルの場合
UDP_PORT = 5000
MESSAGE = "こんにちは！"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE.encode('utf-8'), (UDP_IP, UDP_PORT))
```

### コマンドラインの例（macOS/Linux）

```bash
echo "テストメッセージ" | nc -u 127.0.0.1 5000
```

## 機能

- UDPメッセージの受信監視
- チャイム音の再生（システムボリュームに関係なく大きな音で再生）
- 大きなポップアップ通知の表示
- 通知には受信したメッセージ内容を表示

### 特殊機能

- **AppleScriptによるボリュームコントロール**: システムの音量設定に関わらず、一時的に音量を最大にして通知音を再生し、再生後に元の音量に自動的に戻ります
- **繰り返し再生**: 通知音を5秒間繰り返し再生することで、確実に通知を伝えます

## macOSでの常駐実行

以下の方法で起動時に自動実行される設定ができます：

1. LaunchAgentsフォルダに移動：
```bash
cd ~/Library/LaunchAgents/
```

2. plist設定ファイルを作成：

### システムのPythonを使用する場合
```bash
cat > com.user.chimedaemon.plist << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.chimedaemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/絶対パス/chime_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOL
```

### pyenv virtualenvを使用する場合
```bash
cat > com.user.chimedaemon.plist << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.chimedaemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/ユーザー名/.pyenv/versions/仮想環境名/bin/python</string>
        <string>/絶対パス/chime_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/ユーザー名/.pyenv/bin</string>
    </dict>
</dict>
</plist>
EOL
```

**注意**: 
- `/絶対パス/` は実際のスクリプトの場所に置き換えてください（例: `/Users/ユーザー名/Projects/ChimeDaemon/chime_daemon.py`）
- `ユーザー名` と `仮想環境名` は実際の値に置き換えてください
- pyenvの仮想環境のパスは、以下のコマンドで確認できます：
```bash
pyenv which python
```

3. launchdに登録：
```bash
launchctl load ~/Library/LaunchAgents/com.user.chimedaemon.plist
``` 