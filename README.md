# tomatrick-daily-music

自動的に音楽を生成し、DistroKidにアップロードするツールです。

## 機能

- OpenAIを使用して小学生向けのキーワードを生成
- SunoのAPIを使用して音楽を生成
- DistroKidに自動ログインして音楽をアップロード

## セットアップ

1. 必要なパッケージをインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. 環境変数を設定:
   - `.env.example`をコピーして`.env`を作成
   - 必要なAPIキーとアカウント情報を設定

3. 必要な環境変数:
   - `OPENAI_API_KEY`: OpenAI APIキー
   - `SUNO_API_KEY`: Suno APIキー
   - `DK_EMAIL`: DistroKidのメールアドレス
   - `DK_PASSWORD`: DistroKidのパスワード

## 実行

```bash
python windsurf/scripts/generate_upload.py
```

## 注意事項

- Slack通知機能は実装されていません
- ジャケットアートの自動生成機能は実装されていません（TODO）

## CI/CD

このプロジェクトにはGitHub Actionsを使用したCI/CDワークフローが設定されています。

- テストの自動実行
- コード品質チェック
- テストカバレッジの追跡
- 型チェック

ワークフローは`main`ブランチへのプッシュやプルリクエスト時に実行されます
