from fastapi import FastAPI, Request
from linebot import WebhookParser, LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,
    QuickReply, QuickReplyButton
)
import requests
import json
import base64
import requests
from urllib.parse import urljoin
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

        if line_message=="新規":
           # LINE メッセージの送信
           line_bot_api.push_message(line_user_id, TextSendMessage('"記事タイトル"を入力して'))
           columns_list = []
           columns_list.append(CarouselColumn(title=line_message, text="記事タイトルはこれでいい？", actions=[PostbackAction(label="YES", data=f"NO"), PostbackAction(label="NO", data=f"NO")]))
           #columns_list.append(CarouselColumn(title="タイトルだよ", text="よろしくね", actions=[PostbackAction(label="詳細を表示", data=f"詳細表示"), PostbackAction(label="削除", data=f"削除")]))
           carousel_template_message = TemplateSendMessage(
                                       alt_text='会話ログを表示しています',
                                       template=CarouselTemplate(columns=columns_list)
                                       )
           line_bot_api.reply_message(event.reply_token, messages=carousel_template_message)
    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'
