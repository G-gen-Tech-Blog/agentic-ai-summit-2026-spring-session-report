# 概要
本資料は2026年3月19日にG-genの奥田と今野が登壇した「Agentic AI Summit Spring」のデモとなります。

Google ADK (Agent Development Kit) を使い、議事録テキストから Todo を抽出して Google Calendar に自動登録するエージェントです。
Gemini Enterprise にデプロイをすることを想定しております。

## Agentic AI Summit「Gemini Enterprise × ADKで実現する『業務特化型エージェント』開発の最前線」

- イベントページ: https://cloudonair.withgoogle.com/events/agentic-ai-summit-26-spring/watch?talk=26q1-t2-session1
- 動画: https://youtu.be/j96tz3rCts8?si=rKo7WnTb8YqRBZyl
- 登壇資料: https://services.google.com/fh/files/events/t2-s1_agentic-ai-summit26_spring.pdf

📝 セッションレポート: 作成中<!-- TODO: ブログ公開後に共有予定 -->

## 構成図

![構成図](https://storage.googleapis.com/risa-publicbucket/agentic-ai-summit-demo.png)

## 特徴

- 議事録やメモの自由形式テキストから日時・タイトル・参加者を自動抽出
- Google Calendar へのイベント作成・一覧取得・更新・削除に対応
- Agent Engine 上での OAuth 認証に対応
- Gemini 3.0 Flash をバックエンドに使用

## デプロイ方法

### 前提条件

- Google Cloud プロジェクトが作成済みであること
- Agent Engine API が有効化されていること
- `gcloud` CLI がインストール・認証済みであること
- Gemini Enterprise のライセンスを購入しており、エージェントを登録するアプリが存在すること

### 手順

※詳しい手順は登壇資料、登壇動画をご参考ください。

1. gcloud の設定
```bash
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
```

2. 依存パッケージのインストール

```
pip install -r requirements.txt
```

3. Agent Engine へデプロイ

```bash
adk deploy agent_engine \
  --project=<YOUR_PROJECT_ID> \
  --region=global \
  --display_name="calendar-agent" \
  .
```
4. Gemini Enterprise アプリに登録

## 動作確認

- 2026/03/31 動作確認済み（G-gen奥田）

## 注意事項

> **本リポジトリはデモ・検証目的のコードです。本番環境での利用は想定していません。**
> リトライ処理・エラーハンドリング・レート制限対策などの実装を含んでいないため、全社展開や業務利用を行う場合は十分な設計・テストを行ったうえでご利用ください。
