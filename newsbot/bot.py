import os
import configparser

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

import newsbot.config as config
import newsbot.database as database
import newsbot.network as network


class Bot:
    def __init__(self, a_token=None, a_use_context=None):
        self.db = database.DatabaseController

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

        handler = MessageHandler(Filters.text | Filters.command, self.__handle_message)
        self._dispatcher.add_handler(handler)

        self._main_buttons = [
            [
                'Изменить интервал ⏱',
                'Выбрать топики 📖',
            ]
        ]

        self._states = [
            self.__s_start,
            self.__s_main,
            self.__s_typing_interval,
            self.__s_choosing_topics,
        ]

    @property
    def config(self):
        return dict(self._config['DEFAULT'])

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def stop(self):
        self._updater.stop()

    def __handle_message(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        self.db.add_user_if_there_is_not(user_id)

        user_state = self.db.get_user_state(user_id)
        self._states[user_state](a_update, a_context)

    def __s_start(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        user_name = a_update.effective_user.name

        self.db.set_user_state(user_id, 1)

        text = f'Привет, {user_name}!\nЭтот бот предназначен для получения новостей с habr.com по вашим ' \
               f'предпочтениям.\nВы также можете задать с помощью кнопок интервал отправки новостей и интересующих ' \
               f'для вас топиков новостей.'

        a_context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(self._main_buttons)
        )

    def __s_main(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        user_text = a_update.message.text

        if user_text not in self._main_buttons[0]:
            text = 'Неизвестная команда 🤥. Воспользуйся кнопками ниже!'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(self._main_buttons)
            )
        else:
            if user_text == 'Изменить интервал ⏱':
                self.db.set_user_state(user_id, 2)

                text = 'Введите новое значение интервала отправки новостей.'
                a_context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=ReplyKeyboardMarkup([['Отмена']])
                )
            elif user_text == 'Выбрать топики 📖':
                self.db.set_user_state(user_id, 3)

                text = 'Выберите интересующие вас топики новостей.\n✅ – означает, что топик выбран, ❌ – обратное. Для ' \
                       'того, чтобы выйти, выберите кнопку "Закончить выбор".'
                a_context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=self.__get_keyboard_tor_edit_topics(user_id)
                )

    def __s_typing_interval(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        user_text = a_update.message.text

        if user_text.isdigit():
            self.db.change_user_interval(user_id, user_text)
            self.db.set_user_state(user_id, 1)

            text = f'Интервал отправки новостей успешно изменен. Текущее значение интервала: {user_text}'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(self._main_buttons)
            )
        elif user_text == 'Отмена':
            self.db.set_user_state(user_id, 1)
            interval = self.db.get_user_interval(user_id)

            text = f'Операция по изменению интервала отменена. Текущее значение интервала: {interval}'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(self._main_buttons)
            )
        else:
            text = 'Некорректное значение для интервала! Попробуй еще раз.'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
            )

    def __s_choosing_topics(self, a_update: Update, a_context: CallbackContext):
        user_id = a_update.effective_user.id
        user_topic = a_update.message.text

        if user_topic[:-1] in self._topics:
            user_topic = user_topic[:-1]
            if self.db.has_user_topic(user_id, user_topic):
                self.db.remove_topic_of_user(user_id, user_topic)
                text = f'Топик "{user_topic}" успешно удален!'
            else:
                self.db.add_topic_to_user(user_id, user_topic)
                text = f'Топик "{user_topic}" успешно выбран!'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=self.__get_keyboard_tor_edit_topics(user_id)
            )
        elif user_topic == 'Закончить выбор':
            self.db.set_user_state(user_id, 1)

            text = 'Операция по выбору топиков завершена! Изменения зафиксированы.'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=ReplyKeyboardMarkup(self._main_buttons)
            )
        else:
            text = 'Неизвестный топик 🤥. Для выбора топика воспользуйтесь кнопками!'
            a_context.bot.send_message(
                chat_id=user_id,
                text=text
            )

    def __get_keyboard_tor_edit_topics(self, a_user_id):
        user_chosen_topics = self.db.get_users_topics(a_user_id)

        btns_text = []
        for topic in self._topics:
            if topic in user_chosen_topics:
                btns_text.append(f'{topic}✅')
            else:
                btns_text.append(f'{topic}❌')

        keyboard = []
        tmp = []

        for idx, text in enumerate(btns_text):
            if (idx + 1) % 3 != 0:
                tmp.append(KeyboardButton(text))
            else:
                keyboard.append(tmp.copy())
                tmp.clear()

        if len(tmp) + 1 % 3 == 0:
            keyboard.append(tmp.copy())
            tmp.clear()
        tmp.append(KeyboardButton('Закончить выбор'))
        keyboard.append(tmp)

        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
