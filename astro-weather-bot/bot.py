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
    print(msg)
    if 'location' not in msg:
        pass
    else:
        location = msg['location']
        base_api_url = 'http://202.127.24.18/v4/bin/astro.php?'
        param = {'lon':location['longitude'],'lat':location['latitude'],'output':'internal'}
        query_url = base_api_url+urllib.parse.urlencode(param)
        pic_file,headers=urllib.request.urlretrieve(query_url)
        pic = open(pic_file,'rb')
        bot.sendPhoto(msg['chat']['id'],('astro.png',pic))
        pic.close()
        urllib.request.urlcleanup()



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




