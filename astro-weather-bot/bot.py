import telepot
from telepot.loop import OrderedWebhook
import sys
from flask import Flask, request
import urllib.parse
import urllib.request

"""
python bot.py [port]
port must be one out of 443, 80, 88,    8443
"""

def handler(msg):
    global bot
    if 'location' not in msg['message']:
        pass
    else:
        location = msg['message']['location']
        base_api_url = 'http://202.127.24.18/v4/bin/astro.php?'
        param = {'lon':location['longitude'],'lat':location['latitude'],'output':'internal'}
        query_url = base_api_url+urllib.parse.urlencode(param)
        bot.sendPhoto(msg['message']['chat']['id'],('astro.png',urllib.request.urlopen(query_url)))


with open('token','r') as f:
    token = f.readline()

token = token.strip('/n')
bot = telepot.Bot(token)
port = int(sys.argv[1])
url = 'http://saka.mdzz.info:'+str(port)+'/'+token

app = Flask(__name__)

webhook = OrderedWebhook(bot,handler)

@app.route('/'+token,methods=['POST','GET'])
def pass_update():
    webhook.feed(request.data)
    return 'OK'

if __name__=='__main__':
    try:
        f = open('PUBLICKEY.pem','r')
        bot.setWebhook(url,f)
    except telepot.exception.TooManyRequestsError:
        pass
    finally:
        f.close()
    webhook.run_as_thread()
    app.run(port=port,debug=True)




