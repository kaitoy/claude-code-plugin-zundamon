# Zundamon Plugin for Claude Code

ずんだもんとバイブコーディングしている感じになれるClaude Codeプラグイン。

![screenshot](images/zundamon.gif)

## 機能

語尾が「なのだ」になります。

また、Pythonの標準ライブラリtkinterを使用して、ずんだもんのスプライトを画面に表示する通知を実現します。各通知には専用のずんだもん画像と音声が同時に再生されます。

| フックタイプ | 説明 | 画像 | 音声 |
|---|---|---|---|
| **permission_prompt** | Claudeが権限を要求する際に通知 | zunmon_3015_small.png | ask.wav / oi.wav / decision.wav / ask2.wav / ask3.wav（ランダム） |
| **idle_prompt** | Claudeがアイドル状態で入力待ちの際に通知 | zunmon_3016_small.png | waiting.wav |
| **stop** | Claudeが停止した際に通知 | zunmon_3001_small.png | done.wav / perfect.wav（ランダム） |

通知は画面右下に表示され、クリックまたは `b` キーを押して閉じることもできます。

## プラグイン構造

```
zundamon/
├── plugin.json                # プラグインマニフェスト
├── hooks/
│   └── hooks.json            # hooks設定
├── images/                   # ずんだもんスプライト画像
│   ├── zunmon_3001_small.png # stop用画像
│   ├── zunmon_3015_small.png # permission_prompt用画像
│   └── zunmon_3016_small.png # idle_prompt用画像
├── sounds/                   # 通知音声ファイル
│   ├── ask.wav               # permission_prompt用（ランダム）
│   ├── ask2.wav              # permission_prompt用（ランダム）
│   ├── ask3.wav              # permission_prompt用（ランダム）
│   ├── decision.wav          # permission_prompt用（ランダム）
│   ├── oi.wav                # permission_prompt用（ランダム）
│   ├── done.wav              # stop用（ランダム）
│   ├── perfect.wav           # stop用（ランダム）
│   └── waiting.wav           # idle_prompt用
├── notify.py                 # 通知スクリプト
└── README.md
```

- **plugin.json**: プラグインのメタデータと設定（`userConfig`でユーザー設定を定義）
- **hooks/hooks.json**: Notificationフックの定義（`${CLAUDE_PLUGIN_ROOT}`変数でプラグインルートを参照）
- **images/**: 各フックタイプ用のずんだもんスプライト画像
- **sounds/**: 各フックタイプ用の通知音声（WAV形式）
- **notify.py**: tkinterを使ったスプライト表示と音声再生スクリプト

## 設定

プラグインを有効化する際にClaude Codeが設定値を入力するよう促します。設定後は `claude plugin config zundamon` で変更できます。

| 設定キー | 型 | デフォルト | 説明 |
|---|---|---|---|
| `notification_duration` | 数値（秒） | `60` | 通知画像の表示時間（秒） |
| `voice_enabled` | bool | `true` | 通知時に音声を再生するかどうか |

## インストール

1. プラグインをClaude Codeのプラグインディレクトリに配置:

```bash
# Windowsの場合
cd "%APPDATA%\Claude Code\plugins"
git clone https://github.com/kaitoy/claude-code-plugin-zundamon.git

# macOS/Linuxの場合
cd ~/.config/claude-code/plugins
git clone https://github.com/kaitoy/claude-code-plugin-zundamon.git
```

2. Claude Codeを再起動すると、プラグインが自動的に読み込まれます。

注: tkinterはPythonの標準ライブラリのため、追加の依存関係のインストールは不要です。

## 使い方

### 基本的な使い方

設定が完了すると、Claude Codeが自動的にhooksを実行し、画面右下にずんだもんのスプライトとメッセージを表示します。

通知スクリプトは以下の優先順位でメッセージを決定します:

1. コマンドライン引数 `--message`
2. stdinから受け取ったJSON入力の`message`フィールド
3. デフォルトメッセージ

Claude CodeのHookは自動的にJSONデータをstdin経由でスクリプトに渡すため、hook入力の`message`フィールドが通知に表示されます。

通知ウィンドウをクリックすると、すぐに閉じることができます。

### カスタム通知

スクリプトを直接実行してテストすることもできます:

```bash
# 基本的な通知
python notify.py permission_prompt
python notify.py idle_prompt
python notify.py stop

# コマンドライン引数でカスタムメッセージ
python notify.py permission_prompt --message "カスタムメッセージ"

# 通知の表示時間を変更（秒）
python notify.py idle_prompt --timeout 15

# stdinからJSONを渡す
echo '{"message": "Hookからのメッセージ"}' | python notify.py permission_prompt
```

### JSON入力フォーマット

Claude CodeのHookから渡されるJSON形式:

```json
{
  "message": "Claude is requesting permission to run a command",
  "type": "permission_prompt"
}
```

スクリプトは`message`フィールドを抽出して通知に表示します。

### オプション

- `hook_type`: `permission_prompt`, `idle_prompt`, または `stop`（必須）
- `--message`: カスタム通知メッセージ（stdinのmessageより優先、オプション）
- `--timeout`: 通知の表示時間（秒、デフォルト: 10）

## トラブルシューティング

### 通知が表示されない

1. tkinterが正しくインストールされているか確認:
   ```bash
   python -m tkinter
   ```
   小さなウィンドウが表示されればtkinterは正常に動作しています。

2. スクリプトを直接実行してテスト:
   ```bash
   python notify.py permission_prompt
   ```

3. Pythonのパスが正しいか確認（`python`または`python3`）

### 画像が表示されない

1. `images/`ディレクトリに必要なPNGファイルがあるか確認:
   ```bash
   ls images/zunmon_*_small.png
   ```

2. 画像ファイルのパスが正しいか確認（スクリプトと同じディレクトリ内に`images/`フォルダが必要）

### Windows特有の問題

特になし。tkinterはPythonに標準で含まれています。音声再生には`winsound`（Python標準ライブラリ）を使用するため、追加インストール不要です。

### 音声が再生されない

音声再生にはOS標準のツールを使用します。

- **Windows**: `winsound`（Python標準ライブラリ）— 追加インストール不要
- **macOS**: `afplay`（macOS標準）— 追加インストール不要
- **Linux**: `aplay`（ALSAユーティリティ）— 未インストールの場合:
  ```bash
  # Ubuntu/Debianの場合
  sudo apt-get install alsa-utils
  ```

音声ファイルが見つからない場合は警告を出して通知表示は続行します。

### macOS特有の問題

macOSでは、tkinterを使用するためにPythonのフレームワークビルドが必要な場合があります。

### Linux特有の問題

一部のLinuxディストリビューションでは、tkinterが別パッケージになっている場合があります。

```bash
# Ubuntu/Debianの場合
sudo apt-get install python3-tk

# Fedora/RHELの場合
sudo dnf install python3-tkinter
```

## 動作環境

- Python 3.7以上（tkinter標準搭載、PNG形式サポート）
- Claude Code

注: tkinterのPhotoImageでPNG形式を扱うには、Tk/Tcl 8.6以降が必要です。Python 3.7以降にはTk/Tcl 8.6がバンドルされています。

## ライセンス

MIT License

（ず・ω・きょ）

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。
