import os
import configparser

from telegram import Update
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters

import newsbot.config as config
import newsbot.database as database
import newsbot.network as network


# noinspection PyMethodMayBeStatic
class Bot:
    def __init__(self, a_token=None, a_use_context=None):
        self._config = configparser.ConfigParser()

        if not os.path.exists(config.BOT_SETTINGS_PATH):
            with open(config.BOT_SETTINGS_PATH, 'w') as configfile:
                config.DEFAULT_SETTINGS.write(configfile)
            self._config = config.DEFAULT_SETTINGS
        self._config.read(config.BOT_SETTINGS_PATH)

        self._token = a_token if a_token else self._config['DEFAULT']['token']
        self._use_context = a_use_context if a_use_context else self._config['DEFAULT']['use_context']

        self._updater = Updater(token=self._token, use_context=self._use_context)
        self._dispatcher = self._updater.dispatcher

        echo_handler = MessageHandler(Filters.text & (~Filters.command), self._echo)
        self._dispatcher.add_handler(echo_handler)

    @property
    def config(self):
        return dict(self._config['DEFAULT'])

    def start(self):
        self._updater.start_polling()

    def stop(self):
        self._updater.stop()

    def _echo(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
