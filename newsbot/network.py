import requests

from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


class NewsSiteParser:
    def __init__(self, a_url, a_topic_class):
        """
        :param a_url: URL сайта новостей
        :param a_topic_class: Имя класса объекта, представляющего собой тему новостей
        """

        self._url = a_url
        self._topic_class = a_topic_class
        self._user_agent = UserAgent()
        self._headers = {'accept': '*/*', 'user-agent': self._user_agent.firefox}

    def get_news_topics(self):
        r = requests.get(self._url, headers=self._headers)
        soup = bs(r.text, features='html.parser')
        topics = soup.find_all('a', {'class': self._topic_class})
        return [topic.text.strip() for topic in topics]
