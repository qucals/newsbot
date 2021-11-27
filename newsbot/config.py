import os
import configparser

BOT_SETTINGS_FILE = 'bot_config.ini'
BOT_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), BOT_SETTINGS_FILE)

DEFAULT_SETTINGS = configparser.ConfigParser()
DEFAULT_SETTINGS['DEFAULT'] = {
    'token': 'None',
    'use_context': 'False',
    'news_url': 'https://habr.com/ru/all/',
    'news_topic_class': 'tm-main-menu__item',
}