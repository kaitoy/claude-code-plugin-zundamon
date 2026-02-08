# Zundamon Plugin for Claude Code

ずんだもんとバイブコーディングしている感じになれるClaude Codeプラグイン。

![screenshot](images/zundamon.gif)

## 機能

語尾が「なのだ」になります。

また、Pythonの標準ライブラリtkinterを使用して、ずんだもんのスプライトを画面に表示する通知を実現します。各通知には専用のずんだもん画像が表示されます。

- **permission_prompt**: Claudeが権限を要求する際に通知（画像: zunmon_3015_small.png）
- **permission_request**: Claudeがツールの使用権限を要求する際に通知（画像: zunmon_3015_small.png）
- **idle_prompt**: Claudeがアイドル状態で入力待ちの際に通知（画像: zunmon_3016_small.png）
- **stop**: Claudeが停止した際に通知（画像: zunmon_3001_small.png）

通知は画面右下に表示され、クリックして閉じることもできます。

## プラグイン構造

```
zundamon/
├── plugin.json                # プラグインマニフェスト
├── hooks/
│   └── hooks.json            # hooks設定
├── images/                   # ずんだもんスプライト画像
│   ├── zunmon_3001_small.png # stop用画像
│   ├── zunmon_3015_small.png # permission_prompt/request用画像
│   └── zunmon_3016_small.png # idle_prompt用画像
├── notify.py                 # 通知スクリプト
└── README.md
```

- **plugin.json**: プラグインのメタデータと設定
- **hooks/hooks.json**: Notificationフックの定義（`${CLAUDE_PLUGIN_ROOT}`変数でプラグインルートを参照）
- **images/**: 各フックタイプ用のずんだもんスプライト画像
- **notify.py**: tkinterを使ったスプライト表示スクリプト

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

- `hook_type`: `permission_prompt`, `permission_request`, `idle_prompt`, または `stop`（必須）
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

特になし。tkinterはPythonに標準で含まれています。

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
