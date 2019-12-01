import logging
import os
import random
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from telegram.ext import Updater, CommandHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
sched = BackgroundScheduler()
CRON_SCHEDULE = '0 12-17 * * MON-FRI'

if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def start_handler(bot, update):
    # Creating a handler-function for /sebatstart command 
    logger.info("Chat {} started bot".format(update.effective_chat.id))
    kwargs = {'chat_id': update.effective_chat.id, 'text': "~ kuy sebat kuy ~"}
    sched.add_job(bot.send_message, CronTrigger.from_crontab(CRON_SCHEDULE), kwargs=kwargs, id='sebat-reminder')
    sched.start() if not sched.running else sched.resume()


def stop_handler(bot, update):
    # Creating a handler-function for /sebatstop command
    logger.info("Chat {} stopped bot".format(update.effective_chat.id))
    sched.remove_job('sebat-reminder')
    sched.pause()


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("sebatstart", start_handler))
    updater.dispatcher.add_handler(CommandHandler("sebatstop", stop_handler))

    run(updater)