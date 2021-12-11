import os
import configparser

BOT_SETTINGS_FILE = 'bot_config.ini'
BOT_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), BOT_SETTINGS_FILE)

BOT_DATABASE_PATH = '/database.db'

DEFAULT_SETTINGS = configparser.ConfigParser()
DEFAULT_SETTINGS['DEFAULT'] = {
    'token': 'None',
    'use_context': 'False',
    'news_url': 'https://habr.com/ru/',
    'news_url_topic': 'https://habr.com/ru/flows/',
    'news_topic_class': 'tm-main-menu__item',
    'news_title': 'tm-article-snippet__title tm-article-snippet__title_h1',
    'news_limit_text': 560,
    'news_additional_content_id': 'post-content-body'
}
