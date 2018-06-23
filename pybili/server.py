import DanMuJi
import bili_sender
import bili_config
import thread
from flask import Flask
from flask import request

app = Flask(__name__)
config = bili_config.Config()
sender = bili_sender.Sender(config.cookies)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/check")
def check():
    return sender.isCookieValid()

@app.route('/setcookie.do', methods=['POST', 'GET'])
def setCookie():
    c = request.form['c']
    config.setCookies(c)
    return 'OK'
