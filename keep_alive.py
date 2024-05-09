import datetime
from threading import Thread

from flask import Flask

app = Flask('')

i = 0

@app.route('/')
def main():
    return f"BOT YAŞIYOR! En son zaman:{datetime.datetime.now()}, {i+1}"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
