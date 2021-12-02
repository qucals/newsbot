import os
import configparser

from sqlalchemy import insert, delete, update, select

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, CommandHandler, ConversationHandler

import newsbot.config as config
import newsbot.database as database
import newsbot.network as network


# noinspection PyMethodMayBeStatic
class Bot:
    _MAIN_KEYBOARD = [
        [
            'Изменить интервал отправки новостей',
            'Изменить темы'
        ]
    ]

    def __init__(self, a_token=None, a_use_context=None):
        self._config = configparser.ConfigParser()

        if not os.path.exists(config.BOT_SETTINGS_PATH):
            with open(config.BOT_SETTINGS_PATH, 'w') as configfile:
                config.DEFAULT_SETTINGS.write(configfile)
            self._config = config.DEFAULT_SETTINGS
        self._config.read(config.BOT_SETTINGS_PATH)

        self._token = a_token if a_token else self._config['DEFAULT']['token']
        self._use_context = a_use_context if a_use_context else self._config['DEFAULT']['use_context']

        self._parser = network.NewsSiteParser(self.config['news_url'])
        self._topics = self._parser.get_news_topics(self.config['news_topic_class'])

        self._updater = Updater(token=self._token, use_context=self._use_context)
        self._dispatcher = self._updater.dispatcher

        # change_interval_controller = ConversationHandler('change_interval', self._change_interval_controller)
        change_interval_controller = CommandHandler('change_interval', self.__change_interval_controller)
        self._dispatcher.add_handler(change_interval_controller)

        edit_topics_controller = CommandHandler('edit_topics', self.__edit_topics_controller)
        self._dispatcher.add_handler(edit_topics_controller)

        main_message_controller = MessageHandler(Filters.command, self.__main_message_controller)
        self._dispatcher.add_handler(main_message_controller)

    @property
    def config(self):
        return dict(self._config['DEFAULT'])

    def start(self):
        self._updater.start_polling()

    def stop(self):
        self._updater.stop()

    def add_user_to_database(self, a_id):
        stmt = (
            insert(database.Users).
            values(user_id=a_id)
        )
        database.engine.execute(stmt)

    def is_user_in_database(self, a_id):
        stmt = (
            select(database.Users.user_id).
            where(database.Users.user_id == a_id)
        )
        results = database.engine.execute(stmt).fetchall()
        return len(results) != 0

    def change_user_interval(self, a_id, a_interval):
        stmt = (
            update(database.Users.user_id).
            where(database.Users.user_id == a_id).
            values(interval_send_news=a_interval)
        )
        database.engine.execute(stmt)

    def __change_interval_controller(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_chat.id
        if not self.is_user_in_database(user_id):
            self.add_user_to_database(user_id)
        a_context.bot.send_message(chat_id=a_update.effective_chat.id,
                                   text='Укажите интервал отправки сообщений (в минутах)',
                                   reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Назад', callback_data='Назад')]]))
        interval = ''
        while not (interval.isdigit() or interval == 'Назад'):
            a_context.bot.send_message(chat_id=a_update.effective_chat.id,
                                       text='Некорректное сообщение')
        if interval.isdigit():
            self.change_user_interval(user_id, interval)

    def __edit_topics_controller(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_chat.id
        if not self.is_user_in_database(user_id):
            self.add_user_to_database(user_id)

    def __main_message_controller(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_chat.id
        if not self.is_user_in_database(user_id):
            self.add_user_to_database(user_id)
        a_context.bot.send_message(chat_id=a_update.effective_chat.id,
                                   text=a_update.message.text,
                                   reply_markup=ReplyKeyboardMarkup(self._MAIN_KEYBOARD))
