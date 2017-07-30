import time
import telepot
from telepot.loop import OrderedWebhook
import sys
from flask import Flask, request
import urllib.parse
import urllib.request
from telepot.delegate import per_chat_id, create_open, pave_event_space

"""
python bot.py [port]
port must be one out of 443, 80, 88,    8443
"""

class MessageHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        global bot
#        print(msg)
        if 'location' not in msg:
            pass
        else:
            location = msg['location']
            base_api_url = 'http://202.127.24.18/v4/bin/astro.php?'
            param = {'lon':location['longitude'],'lat':location['latitude'],'output':'internal'}
            query_url = base_api_url+urllib.parse.urlencode(param)
            pic_file,headers=urllib.request.urlretrieve(query_url, 'test.png')
            pic = open(pic_file,'rb')
            bot.sendPhoto(msg['chat']['id'], pic)
            pic.close()
            urllib.request.urlcleanup()



with open('token','r') as f:
    token = f.readline()

token = token.rstrip()
#bot = telepot.Bot(token)
bot = telepot.DelegatorBot(token, [
    pave_event_space()(
        per_chat_id(), create_open, MessageHandler, timeout=10),
])
port = int(sys.argv[1])
url = 'http://saka.mdzz.info:'+str(port)+'/'+token

app = Flask(__name__)

webhook = OrderedWebhook(bot)
URL = "https://saka.mdzz.info:8443/webhooks"

@app.route('/webhooks',methods=['POST','GET'])
def pass_update():
    webhook.feed(request.data)
    return 'OK'

if __name__=='__main__':
    webhook.run_as_thread()
    app.run(port=port,host='0.0.0.0',ssl_context=('PUBLICKEY.pem','/home/ubuntu/.ssh/YOURPRIVATE.key'))




