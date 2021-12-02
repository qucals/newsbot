import os
import configparser

from sqlalchemy import insert, delete, update, select

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, CommandHandler, ConversationHandler

import newsbot.config as config
import newsbot.database as database
import newsbot.network as network


# noinspection PyMethodMayBeStatic
class Bot:
    _MAIN_KEYBOARD = [
        [
            '/interval',
            '/topics'
        ]
    ]

    CHANGE_INTERVAL, CHANGE_TOPICS, TYPING_INTERVAL, TYPING_TOPICS = range(4)

    def __init__(self, a_token=None, a_use_context=None):
        self.db_controller = DatabaseController

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

        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('interval', self.__change_interval),
                          CommandHandler('topics', self.__edit_topics)],
            states={
                self.CHANGE_INTERVAL: [CommandHandler('interval',
                                                      self.__change_interval)],
                self.CHANGE_TOPICS: [CommandHandler('topics', self.__edit_topics)],
                self.TYPING_INTERVAL: [MessageHandler(Filters.regex('^[0-9]+$'), self.__typing_interval)],
                self.TYPING_TOPICS: [MessageHandler(Filters.regex('\\w+') & ~Filters.command, self.__typing_topics)],
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)]
        )
        self._dispatcher.add_handler(self.conv_handler)

        # change_interval_controller = ConversationHandler('change_interval', self._change_interval_controller)
        # change_interval_controller = CommandHandler('change_interval', self.__change_interval)
        # self._dispatcher.add_handler(change_interval_controller)

        # edit_topics_controller = CommandHandler('edit_topics', self.__edit_topics)
        # self._dispatcher.add_handler(edit_topics_controller)

        self._dispatcher.add_handler(CommandHandler('start', self.__start))

    @property
    def config(self):
        return dict(self._config['DEFAULT'])

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def stop(self):
        self._updater.stop()

    def __start(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        self.db_controller.add_user_if_there_is_not(user_id)

        # TODO: Изменить текст сообщения
        a_context.bot.send_message(chat_id=user_id,
                                   text='Привет!',
                                   reply_markup=ReplyKeyboardMarkup(self._MAIN_KEYBOARD))

    def __change_interval(self, a_update: Update, a_context: CallbackContext):
        text = 'Введите интервал отправки сообщения.'
        a_context.bot.send_message(chat_id=a_update.effective_user.id,
                                   text=text,
                                   reply_markup=ReplyKeyboardMarkup([['/cancel']]))
        return self.TYPING_INTERVAL

    def __typing_interval(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        if not a_update.message.text.isdigit():
            text = 'Некорректное значение, попробуйте заново!'
            a_context.bot.send_message(chat_id=user_id,
                                       text=text,
                                       reply_markup=ReplyKeyboardMarkup([['/cancel']]))
            return self.TYPING_INTERVAL
        else:
            text = 'Значение успешно обновлено!'
            self.db_controller.change_user_interval(user_id, text)
            a_context.bot.send_message(chat_id=user_id,
                                       text=text,
                                       reply_markup=ReplyKeyboardMarkup(self._MAIN_KEYBOARD))
            return ConversationHandler.END

    def __edit_topics(self, a_update: Update, a_context: CallbackContext):
        return self.TYPING_TOPICS

    def __typing_topics(self, a_update: Update, a_context: CallbackContext):
        return ConversationHandler.END

    def __cancel(self, a_update: Update, a_context: CallbackContext):
        a_context.bot.send_message(chat_id=a_update.effective_chat.id,
                                   reply_markup=ReplyKeyboardMarkup(self._MAIN_KEYBOARD))
        return ConversationHandler.END


class DatabaseController:
    @staticmethod
    def add_user(a_id):
        stmt = (
            insert(database.Users).
            values(user_id=a_id)
        )
        database.engine.execute(stmt)

    @staticmethod
    def is_there_user(a_id):
        stmt = (
            select(database.Users.user_id).
            where(database.Users.user_id == a_id)
        )
        results = database.engine.execute(stmt).fetchall()
        return len(results) != 0

    @staticmethod
    def add_user_if_there_is_not(a_id):
        if not DatabaseController.is_there_user(a_id):
            DatabaseController.add_user(a_id)

    @staticmethod
    def change_user_interval(a_id, a_interval):
        stmt = (
            update(database.Users.user_id).
            where(database.Users.user_id == a_id).
            values(interval_send_news=a_interval)
        )
        database.engine.execute(stmt)

    @staticmethod
    def get_users_topics(a_id):
        stmt = (
            select(database.UserTopics.chosen_topic).
            where(database.UserTopics.user_id == a_id)
        )
        cursor = database.engine.execute(stmt)
        return cursor.fetchall()

    @staticmethod
    def add_topic_to_user(a_id, a_topic):
        stmt = (
            insert(database.UserTopics).
            values(user_id=a_id, chosen_topic=a_topic)
        )
        database.engine.execute(stmt)

    @staticmethod
    def remove_topic_of_user(a_id, a_topic):
        stmt = (
            delete(database.UserTopics).
            where(database.UserTopics.user_id == a_id).
            where(database.UserTopics.chosen_topic == a_topic)
        )
        database.engine.execute(stmt)
