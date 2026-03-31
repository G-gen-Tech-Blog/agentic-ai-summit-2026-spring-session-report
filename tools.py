import os
import logging
import traceback
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.adk.tools import ToolContext

# ロガーの設定
logging.basicConfig(level=logging.INFO)

# ============================================================================
# 認証・サービス生成 (Agent Engine 対応版)
# ============================================================================
def get_calendar_service(tool_context: ToolContext):
    """
    Agent Engine 環境で Google Calendar サービスを認証・生成します。
    """
    try:
        # 1. 環境変数から管理画面で設定した ID を取得
        auth_id = os.getenv("AUTH_ID")
        
        # --- デバッグログ ---
        logging.info("===== OAuth Debug Start =====")
        logging.info(f"AUTH_ID (Environment Variable): {auth_id}")
        
        if tool_context and tool_context.state:
            # State オブジェクトはシリアライズ可能なため、そのままログ出力して中身を確認
            logging.info(f"Current State contents: {tool_context.state}")
        else:
            logging.error("tool_context.state is None or empty. User may need to login.")
        logging.info("===== OAuth Debug End =====")
        # ------------------

        # 2. トークンの取得を試みる
        # まず環境変数の ID で試し、見つからなければ "authentication" で試す
        access_token = tool_context.state.get(auth_id)
        if not access_token:
            access_token = tool_context.state.get("authentication")
            if access_token:
                logging.info("Token found using fallback key: 'authentication'")

        # 3. トークンが全く見つからない場合の処理
        if not access_token:
            raise ValueError(
                f"認証トークンが取得できませんでした。探したキー: '{auth_id}', 'authentication'。 "
                "チャット画面で Google ログインを完了させているか確認してください。"
            )

        # 4. 取得したトークンでカレンダーサービスを構築
        creds = Credentials(token=access_token)
        return build("calendar", "v3", credentials=creds)

    except Exception as e:
        # 詳細なトレースバックをログに残す
        logging.error(f"Error in get_calendar_service: {str(e)}")
        traceback.print_exc()
        raise
# ============================================================================
# ツール関数群
# ============================================================================

def read_todo_file(file_path: str, tool_context: ToolContext = None) -> dict:
    """テキストファイルを読み込んで内容を返す。

    Args:
        file_path: 読み込むファイルのパス。
        tool_context: (使用しませんがインターフェース統一のため維持)

    Returns:
        ファイル内容を含む dict。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except FileNotFoundError:
        return {"status": "error", "message": f"ファイルが見つかりません: {file_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_calendar_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    tool_context: ToolContext, # Agent Engine
    description: str = "",
    timezone: str = "Asia/Tokyo",
    attendees: list[str] | None = None,
) -> dict:
    """Google Calendar にイベントを作成する。"""
    try:
        # 認証サービス取得 (引数の tool_context を渡す)
        service = get_calendar_service(tool_context)

        # 1. 入力のクリーニング（空白削除）
        s_dt = start_datetime.strip()
        e_dt = end_datetime.strip()

        # 2. 終日イベントかどうかの判定ロジック
        # "T" がなく、かつ ":" も含まれていなければ終日（日付のみ）とみなす
        is_all_day = ("T" not in s_dt) and (":" not in s_dt)

        if is_all_day:
            # 念のため "/" を "-" に置換
            s_dt = s_dt.replace("/", "-")
            e_dt = e_dt.replace("/", "-")
            
            event_body = {
                "summary": summary,
                "description": description,
                "start": {"date": s_dt},
                "end": {"date": e_dt},
            }
        else:
            # 日時の場合、スペース区切りを "T" に修正
            if " " in s_dt:
                s_dt = s_dt.replace(" ", "T")
            if " " in e_dt:
                e_dt = e_dt.replace(" ", "T")

            event_body = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": s_dt, "timeZone": timezone},
                "end": {"dateTime": e_dt, "timeZone": timezone},
            }

        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        # 実行
        event = service.events().insert(calendarId="primary", body=event_body).execute()

        return {
            "status": "success",
            "event_id": event["id"],
            "summary": event["summary"],
            "html_link": event["htmlLink"],
        }

    except HttpError as e:
        error_content = e.content.decode("utf-8")
        logging.error(f"[API Error Detail]: {error_content}")
        return {"status": "error", "message": f"Google API Error: {e.resp.status}", "detail": error_content}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_calendar_events(
    tool_context: ToolContext, # Agent Engine
    max_results: int = 10, 
) -> dict:
    """直近のカレンダーイベント一覧を取得する。"""
    try:
        service = get_calendar_service(tool_context)
        now = datetime.now(timezone.utc).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        event_list = []
        for event in events:
            # start.dateTime がない場合は start.date (終日) を取得
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(
                {
                    "summary": event.get("summary", "(タイトルなし)"),
                    "start": start,
                    "id": event["id"],
                }
            )

        return {"status": "success", "events": event_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_calendar_event(
    tool_context: ToolContext, # Agent Engine
    event_id: str,
    summary: str = None,
    start_datetime: str = None,
    end_datetime: str = None,
    description: str = None,
    location: str = None,
    attendees: list[str] = None,
    timezone: str = "Asia/Tokyo",
) -> dict:
    """既存のイベントを更新する。"""
    try:
        service = get_calendar_service(tool_context)

        # 1. 現在のイベント情報を取得
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # 2. 変更がある項目だけ上書き
        if summary is not None:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location
        if attendees is not None:
            event["attendees"] = [{"email": email} for email in attendees]

        # 3. 日時の変更処理
        if start_datetime and end_datetime:
            s_dt = start_datetime.strip()
            e_dt = end_datetime.strip()
            
            # 終日判定
            is_all_day = ("T" not in s_dt) and (":" not in s_dt)

            if is_all_day:
                s_dt = s_dt.replace("/", "-")
                e_dt = e_dt.replace("/", "-")
                event["start"] = {"date": s_dt}
                event["end"] = {"date": e_dt}
                # dateTimeフィールドが残っているとエラーになる場合があるため消去
                event["start"].pop("dateTime", None)
                event["end"].pop("dateTime", None)
            else:
                if " " in s_dt: s_dt = s_dt.replace(" ", "T")
                if " " in e_dt: e_dt = e_dt.replace(" ", "T")
                event["start"] = {"dateTime": s_dt, "timeZone": timezone}
                event["end"] = {"dateTime": e_dt, "timeZone": timezone}
                # dateフィールドが残っているとエラーになる場合があるため消去
                event["start"].pop("date", None)
                event["end"].pop("date", None)

        # 4. 更新を実行
        updated_event = service.events().update(
            calendarId="primary", eventId=event_id, body=event
        ).execute()

        return {
            "status": "success",
            "event_id": updated_event["id"],
            "summary": updated_event["summary"],
            "html_link": updated_event["htmlLink"],
            "message": "イベントを更新しました。",
        }

    except HttpError as e:
        error_content = e.content.decode("utf-8")
        logging.error(f"[API Error Detail]: {error_content}")
        return {"status": "error", "message": f"Google API Error: {e.resp.status}", "detail": error_content}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_calendar_event(
    event_id: str,
    tool_context: ToolContext, # Agent Engine
) -> dict:
    """Google Calendar からイベントを削除する。"""
    try:
        service = get_calendar_service(tool_context)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": "success", "message": f"イベント(ID: {event_id}) を削除しました。"}
    except HttpError as e:
        return {"status": "error", "message": f"Google API Error: {e.resp.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}