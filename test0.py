from fastapi import FastAPI, Request
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage
import os

LINE_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(LINE_CHANNEL_SECRET)
app = FastAPI()


@app.post('/')
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get('X-Line-Signature', '')

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode('utf-8'), signature)

    # 各イベントの処理（※1つの Webhook に複数の Webhook イベントオブジェっｚクトが含まれる場合あるため）
    for event in events:
        if event.type != 'message':
            continue
        if event.message.type != 'text':
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text


        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(line_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'
