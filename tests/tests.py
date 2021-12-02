from __future__ import absolute_import

import unittest
import os

from newsbot import config
from newsbot.network import NewsSiteParser

config.BOT_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), config.BOT_SETTINGS_FILE)
config.DEFAULT_SETTINGS['DEFAULT']['token'] = '2130893067:AAFL3ERuk30SIcbONhAOV0KZW4PLFzR2D1A'
config.BOT_DATABASE_PATH = '/' + os.path.join(os.path.dirname(__file__), 'database.db')

from newsbot import bot


class BotTest(unittest.TestCase):
    def setUpClass(cls):
        if os.path.exists(config.BOT_DATABASE_PATH):
            os.remove(config.BOT_DATABASE_PATH)

    def setUp(self):
        if os.path.exists(config.BOT_SETTINGS_PATH):
            os.remove(config.BOT_SETTINGS_PATH)
        self.default_user_id = '@totalbooy'

    def tearDown(self):
        if os.path.exists(config.BOT_SETTINGS_PATH):
            os.remove(config.BOT_SETTINGS_PATH)

    def test_create_and_read_config(self):
        """
        Тест: конфигурационный файл создается и считывается
        """

        bot_ = bot.Bot()

        self.assertEqual('2130893067:AAFL3ERuk30SIcbONhAOV0KZW4PLFzR2D1A', bot_.config['token'])
        self.assertEqual('False', bot_.config['use_context'])

    def test_can_read_topics_from_site(self):
        """
        Тест: считываются темы новостей с сайта
        """

        bot_ = bot.Bot()
        parser = NewsSiteParser(bot_.config['news_url'])

        expected_topics = ['Все потоки', 'Разработка', 'Администрирование',
                           'Дизайн', 'Менеджмент', 'Маркетинг', 'Научпоп']
        received_topics = parser.get_news_topics(bot_.config['news_topic_class'])

        self.assertEqual(expected_topics, received_topics)


if __name__ == '__main__':
    unittest.main()
