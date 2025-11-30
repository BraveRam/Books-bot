from handlers import bot
#from flask import Flask, request
import telebot
import helpers.config as config 
import os

TOKEN = config.BOT_TOKEN
"""server = Flask(__name__)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    if update:
        bot.process_new_messages([update])
        
    return "ok", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://flask.tolasaa.repl.co/' + TOKEN)
    return "ok", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
"""
if __name__ == "__main__":
    print("The bot starts running...")
    bot.infinity_polling()
