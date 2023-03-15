

"""def send_msg(msg, time, number='+447899688460' ):
    pywhatkit.sendwhatmsg(number, msg, time[0], time[1])

if __name__ == '__main__':
    send_msg('still logged in', (21, 50))
"""

from flask import Flask, request, jsonify
from test import Ultrawebhook
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    if request.method == 'POST':
        bot = Ultrawebhook(request.json)
        return bot.processing()

if(__name__) == '__main__':
    app.run()