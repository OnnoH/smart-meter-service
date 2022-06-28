from config import Config
from smart_meter import SmartMeter
from telegram import Telegram
from flask import Flask, jsonify


config = Config('config.yml').config
smart_meter = SmartMeter(config.get('smart-meter'))
app = Flask(__name__)


@app.route('/smart-meter', methods=['GET'])
def get():
    response = jsonify(Telegram(smart_meter.get_telegram()).__dict__())
    response.status_code = 200
    response.mimetype = 'application/json'

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
