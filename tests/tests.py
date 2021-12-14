from __future__ import absolute_import

import unittest
import os

from newsbot import config
from newsbot.network import NewsSiteParser

config.BOT_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), config.BOT_SETTINGS_FILE)
config.DEFAULT_SETTINGS['DEFAULT']['token'] = '2130893067:AAFL3ERuk30SIcbONhAOV0KZW4PLFzR2D1A'
config.BOT_DATABASE_PATH = '/' + os.path.join(os.path.dirname(__file__), 'database.db')

from newsbot import bot
from newsbot import database


class BotTest(unittest.TestCase):
    @classmethod
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


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = database.DatabaseController()
        self.config = config.DEFAULT_SETTINGS['DEFAULT']

    def test_add_user_and_topic(self):
        """
        Тест: добавление пользователя и топика в систему
        """

        self.db.add_user_if_not_exists(1)
        self.db.add_topic_if_not_exists('some_topic')

        user = self.db.get_user(1)
        topic = self.db.get_topic('some_topic')

        self.assertNotEqual(None, user)
        self.assertNotEqual(None, topic)

    def test_add_topic_and_post_to_user(self):
        """
        Тест: можно добавить топик пользователю и просмотренную запись
        """

        self.db.add_user_if_not_exists(1)
        self.db.add_topic_if_not_exists('some_topic')

        self.db.add_topic_to_user(a_user_id=1, a_topic_name='some_topic')
        self.db.add_shown_post(a_user_id=1, a_topic_name='some_topic', a_post_id=1)

        has_user_topic = self.db.has_user_topic(a_user_id=1, a_topic_name='some_topic')
        posts = self.db.get_user_shown_posts(a_user_id=1, a_topic_name='some_topic')

        self.assertTrue(has_user_topic)
        self.assertEqual(1, len(posts))


    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(config.BOT_DATABASE_PATH):
            os.remove(config.BOT_DATABASE_PATH)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.config = config.DEFAULT_SETTINGS['DEFAULT']

    def test_can_read_topics_from_site(self):
        """
        Тест: считываются темы новостей с сайта
        """

        parser = NewsSiteParser(self.config['news_url'])

        expected_topics = ['Все потоки', 'Разработка', 'Администрирование',
                           'Дизайн', 'Менеджмент', 'Маркетинг', 'Научпоп']
        received_topics = parser.get_news_topics(self.config['news_topic_class'])

        self.assertEqual(expected_topics, received_topics)


if __name__ == '__main__':
    unittest.main()
