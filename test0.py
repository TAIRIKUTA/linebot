from fastapi import FastAPI, Request
from linebot import WebhookParser, LineBotApi
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
handler =  WebhookParser(LINE_CHANNEL_SECRET)
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
    if re.search(r"YES", postback_msg):
        show_num = int(re.search(r"都道府県を表示&num=([0-9]+)", postback_msg).group(1))
        columns_list = []
        if show_num >= 5:
            for prefecture, capital in zip(df["都道府県"][9*show_num:], df["県庁所在地"][9*show_num:]):
                columns_list.append(CarouselColumn(title=f"{prefecture}", text="県庁所在地を表示しますか", actions=[PostbackAction(label="表示します", data=f"{prefecture}の県庁所在地は{capital}です")]))
            carousel_template_message = TemplateSendMessage(
                            alt_text='都道府県について表示しています',
                            template=CarouselTemplate(columns=columns_list)
                            )
            line_bot_api.reply_message(event.reply_token, messages=carousel_template_message)
        else:
            for prefecture, capital in zip(df["都道府県"][9*show_num:9*show_num+9], df["県庁所在地"][9*show_num:9*show_num+9]):
                columns_list.append(CarouselColumn(title=f"{prefecture}", text="県庁所在地を表示しますか", actions=[PostbackAction(label="表示します", data=f"{prefecture}の県庁所在地は{capital}です")]))
            columns_list.append(CarouselColumn(title=f"次を表示する", text="次へ", actions=[PostbackAction(label="次の都道府県を表示", data=f"都道府県を表示&num={show_num + 1}")]))
            carousel_template_message = TemplateSendMessage(
                            alt_text='都道府県について表示しています',
                            template=CarouselTemplate(columns=columns_list)
                            )
            line_bot_api.reply_message(event.reply_token, messages=carousel_template_message)

    if postback_msg == "キャンセル":
        messages = TextSendMessage(text="キャンセルしました")
        line_bot_api.reply_message(event.reply_token, messages=messages)

    if re.search(r".+の県庁所在地は.+です", postback_msg):
        text = re.search(r"(.+の県庁所在地は.+です)", postback_msg).group(1)
        messages = TextSendMessage(text=text)
        line_bot_api.reply_message(event.reply_token, messages=messages)

def make_quick_reply(token, text):
    items = []
    items.append(QuickReplyButton(action=PostbackAction(label='YES', data='YES')))
    items.append(QuickReplyButton(action=PostbackAction(label='キャンセル', data='キャンセル')))
    messages = TextSendMessage(text=text,
                            quick_reply=QuickReply(items=items))
    line_bot_api.reply_message(token, messages=messages)
