from fastapi import FastAPI, Request
from linebot import WebhookParser, LineBotApi,WebhookHandler
from flask import Flask, request, abort
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction
import os
import re
import pandas as pd

LINE_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = FastAPI()

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
# メッセージを受け取った時のアクション
@handler.add(MessageEvent, message=TextMessage)
def send_infomation(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    msg = event.message.text
    if msg == "新規":
        make_quick_reply(event.reply_token, "新規投稿しますか？")
    elif msg == "更新":
        make_quick_reply(event.reply_token, "投稿記事を更新しますか？")
    else:
        line_bot_api.push_message(line_user_id, TextSendMessage("無効"))

# PostbackActionがあった時のアクション
@handler.add(PostbackEvent)
def on_postback(event):
    postback_msg = event.postback.data

    if postback_msg == "キャンセル":
        messages = TextSendMessage(text="キャンセルしました")
        line_bot_api.reply_message(event.reply_token, messages=messages)


def make_quick_reply(token, text):
    items = []
    items.append(QuickReplyButton(action=PostbackAction(label='YES', data='YES')))
    items.append(QuickReplyButton(action=PostbackAction(label='キャンセル', data='キャンセル')))
    messages = TextSendMessage(text=text,
                            quick_reply=QuickReply(items=items))
    line_bot_api.reply_message(token, messages=messages)
