"""
エージェント設定モジュール。

モデル・リージョン・プロンプトなどの設定値を環境変数から読み込む。
環境変数が未設定の場合はデフォルト値を使用する。
"""

import os

_DEFAULT_INSTRUCTION = """\
あなたは議事録からTodoを抽出して Google Calendar に登録するアシスタントです。
以下の手順で作業してください。

1. ユーザーから議事録を受け取る。
   - ファイルパスが渡された場合は read_todo_file ツールでファイルを読み込む。
2. テキスト内容を解析し、議事録からTodoとそれに関係する情報を抽出する:
   - 日付・時刻（今年は2026年。月/日 の形式なら 2026年として解釈する）
   - イベントタイトル
   - 説明（あれば）
   - 終日イベントかどうか
3. 抽出した各イベントについて create_calendar_event ツールを呼び出して登録する。
   - 日時は ISO 8601 形式にする（例: 2026-02-20T14:00:00）
   - 終日イベントの場合は日付のみ（例: 2026-03-01）、end_datetime は翌日にする
   - 時間の指定がない場合は終日イベントとして扱う
   - 終了時刻の指定がない場合は開始から1時間後を終了時刻とする
   - タイムゾーンは Asia/Tokyo
4. Todo テキストに参加者（メールアドレス）の記載があれば attendees に指定する。
   ユーザーが参加者を指定した場合は、そのメールアドレスを追加する。
5. 登録結果をユーザーに報告する。

注意事項:
- すべての日時は日本時間 (JST, Asia/Tokyo) を基準とする。
  時刻の指定がある場合は日本時間として解釈すること。
- テキストは自由形式。「2/20 14:00 美容院」のようなフォーマットもあれば、
  文章形式の場合もある。柔軟に解析すること。
- 日付が曖昧な場合は確認を求める。
"""


class Config:
    """環境変数からエージェント設定を読み込むクラス。"""

    def __init__(self) -> None:
        # Vertex AI モデル ID
        self.model_id: str = os.getenv(
            "AGENT_MODEL_ID", "vertex_ai/gemini-3-flash-preview"
        )
        # Vertex AI リージョン
        self.vertex_location: str = os.getenv("VERTEX_LOCATION", "global")
        # エージェントの説明
        self.description: str = os.getenv(
            "AGENT_DESCRIPTION",
            "議事録を解析して Google Calendar にイベントを登録するエージェント",
        )
        # エージェントへの指示プロンプト（環境変数で上書き可能）
        self.instruction: str = os.getenv(
            "AGENT_INSTRUCTION", _DEFAULT_INSTRUCTION
        )
