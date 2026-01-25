# Zundamon Plugin for Claude Code

ずんだもんとバイブコーディングしている感じになれるClaude Codeプラグイン。

![screenshot](images/zundamon.gif)

## 機能

語尾が「なのだ」になります。

また、Pythonの[Plyer](https://github.com/kivy/plyer)ライブラリを使用して、クロスプラットフォームなデスクトップ通知を実現します。各通知には専用のアイコンが表示されます。

- **permission_prompt**: Claudeが権限を要求する際に通知（アイコン: zunmon_3015.png）
- **idle_prompt**: Claudeがアイドル状態で入力待ちの際に通知（アイコン: zunmon_3016.png）
- **stop**: Claudeが停止した際に通知（アイコン: zunmon_3001.png）

## プラグイン構造

```
zundamon/
├── plugin.json           # プラグインマニフェスト
├── hooks/
│   └── hooks.json       # hooks設定
├── images/              # 通知アイコン
│   ├── zunmon_3001.ico  # stop用アイコン
│   ├── zunmon_3015.ico  # permission_prompt用アイコン
│   └── zunmon_3016.ico  # idle_prompt用アイコン
├── notify.py            # 通知スクリプト
├── requirements.txt     # Python依存関係
└── README.md
```

- **plugin.json**: プラグインのメタデータと設定
- **hooks/hooks.json**: Notificationフックの定義（`${CLAUDE_PLUGIN_ROOT}`変数でプラグインルートを参照）
- **images/**: 各フックタイプ用のアイコン画像
- **notify.py**: Plyerを使った通知スクリプト（アイコン表示機能付き）

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

2. 依存関係をインストール:

```bash
cd claude-code-plugin-zundamon
pip install -r requirements.txt
```

3. Claude Codeを再起動すると、プラグインが自動的に読み込まれます。

## 使い方

### 基本的な使い方

設定が完了すると、Claude Codeが自動的にhooksを実行し、デスクトップ通知を表示します。

通知スクリプトは以下の優先順位でメッセージを決定します:

1. コマンドライン引数 `--message`
2. stdinから受け取ったJSON入力の`message`フィールド
3. デフォルトメッセージ

Claude CodeのHookは自動的にJSONデータをstdin経由でスクリプトに渡すため、hook入力の`message`フィールドが通知に表示されます。

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

1. Plyerが正しくインストールされているか確認:
   ```bash
   pip show plyer
   ```

2. スクリプトを直接実行してテスト:
   ```bash
   python notify.py permission_prompt
   ```

3. Pythonのパスが正しいか確認（`python`または`python3`）

### アイコンが表示されない

1. `images/`ディレクトリに必要なPNGファイルがあるか確認:
   ```bash
   ls images/zunmon_*.ico
   ```

2. アイコンファイルのパスが正しいか確認（スクリプトと同じディレクトリ内に`images/`フォルダが必要）

3. プラットフォームによってはアイコン表示をサポートしていない場合があります

### Windows特有の問題

Windows 10/11では、通知設定でPythonまたはターミナルからの通知が許可されているか確認してください。

### macOS特有の問題

macOSでは、ターミナルアプリに通知の権限が必要な場合があります。
システム環境設定 > 通知 から設定してください。

### Linux特有の問題

通知デーモン（notification-daemon, dunst等）が実行されているか確認してください。

```bash
# Ubuntu/Debianの場合
sudo apt-get install libnotify-bin
```

## 動作環境

- Python 3.6以上
- Plyer 2.1.0以上
- Claude Code

## ライセンス

MIT License

（ず・ω・きょ）

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。
