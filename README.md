# 概要
本資料は2026年3月19日にG-genの奥田と今野が登壇した「Agentic AI Summit Spring」のデモとなります。

Google ADK (Agent Development Kit) を使い、議事録テキストから Todo を抽出して Google Calendar に自動登録するエージェントです。
Gemini Enterprise にデプロイをすることを想定しております。

## Agentic AI Summit「Gemini Enterprise × ADKで実現する『業務特化型エージェント』開発の最前線」

- イベントページ: https://cloudonair.withgoogle.com/events/agentic-ai-summit-26-spring/watch?talk=26q1-t2-session1
- 動画: https://youtu.be/j96tz3rCts8?si=rKo7WnTb8YqRBZyl
- 登壇資料: https://services.google.com/fh/files/events/t2-s1_agentic-ai-summit26_spring.pdf

📝 セッションレポート: https://blog.g-gen.co.jp/entry/agentic-ai-summit-2026-spring-session-report

## 構成図

![構成図](https://cdn-ak.f.st-hatena.com/images/fotolife/g/ggen-sugimura/20260410/20260410090036.png)

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

## ⚠️ LiteLLM Security Notice

LiteLLM v1.82.7 / v1.82.8 は、サプライチェーン攻撃（TeamPCP）により侵害されました（2026年3月24日）。
本リポジトリは v1.83.0（攻撃後の正規リリース、2026年3月31日公開）にピン留めしています。

### ご利用前に必ず確認してください

1. インストール後、`.pth` ファイルが存在しないことを確認：
```bash
   find $(python -c "import site; print(site.getsitepackages()[0])") -name "litellm_init.pth"
```
2. インストールされたバージョンが想定通りであることを確認：
```bash
   pip show litellm | grep Version
```

### 参考情報

- [LiteLLM 公式セキュリティアップデート](https://docs.litellm.ai/blog/security-update-march-2026)
- [GitHub Issue #24518（タイムライン）](https://github.com/BerriAI/litellm/issues/24518)