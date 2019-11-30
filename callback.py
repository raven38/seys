import falcon
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, BaseSize,
    )
from time import sleep
import tempfile
import os
from deel.deel import *
from deel.network import *
from deel.commands import *
from deel.tensor import *
import string
import random
import credentials

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def generate_random_str(length, chars=None):
    if chars is None:
        chars = string.digits + string.ascii_letters
    return ''.join([random.choice(chars) for i in range(length)])

class Resource(object):
    def on_post(self, req, resp):
#        print(req.headers)
        signature = req.headers['X-LINE-SIGNATURE']
        body = req.stream.read()
        body = body.decode('utf-8')
        try:
            handler.handle(body, signature)
        except InvalidSignatureError as e:
            print(e)
#            abort(400)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
#    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='image'))
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('/tmp/' + generate_random_str(10), 'wb') as tf:
#    with tempfile.NamedTemporaryFile(delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tf_path = tf.name
    print('tf_path', tf_path)
    dist_path = tf_path + '.jpg'
    dist_name = os.path.basename(dist_path)
    print('dist_path', dist_path)    
    os.rename(tf_path, dist_path)
    if os.path.exists(dist_path):
        print('file exists')
    print('dist_name', dist_name)
    CNN.Input(dist_path)
    CNN.classify()
    output = ""
    t = LabelTensor(Tensor.context)
    for rank, (score, name) in enumerate(t.content[:5], start=1):
        output += '#{0:d} {1} {2:4.1f}%\n'.format(rank, name, score*100)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=output))
#    line_bot_api.reply_message(
#        event.reply_token,
#        ImageSendMessage(
#            original_content_url='http://samolet-tk.ru/prefix/09ab747132071f7e6f7280c281c2ee51.jpg',
#            preview_image_url='http://clip.hd-krupno.ru/images/TQLEEXOWG7_xBFS6UnE6wiLjE_VPYEvmVEmU7PL9RFwjmHKW5BuYA4ajJRsQZ3mI8pqraGqtrGI9Dd7qRE5qw2Ga8x82WRl3.jpg'
#            )
#    )

deel = Deel()
CNN = GoogLeNet()
print('')
print('setup')
print('')
app = falcon.API()
app.add_route('/callback', Resource())
    
