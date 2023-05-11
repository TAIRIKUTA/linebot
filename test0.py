from fastapi import FastAPI, Request
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage

LINE_CHANNEL_ACCESS_TOKEN = 'dV3KYxrI2IA21lg6wwUOr9Gm9Jw8xVxlrt2/HO479tuI5t9ALkjt4KhS627+KOLmePUSBwMQYbZDGbHRrFjOTMrF/WyBhY2xJog321Pb3EWwd4FoHGlg0ZPzWrXtQq0O/MxleYUT7A+T2ccyYMpg9QdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '166564241d6d37868b6d043b6166a0dc'


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

        print(line_message)
        line_bot_api.push_message(line_user_id,TextSendMessage(text='Hello World!'))
    #LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'
