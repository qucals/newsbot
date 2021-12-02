import requests

from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


class NewsSiteParser:
    def __init__(self, a_url):
        self._url = a_url
        self._user_agent = UserAgent()
        self._headers = {'accept': '*/*', 'user-agent': self._user_agent.safari}

    def get_news_topics(self, a_topic_class):
        r = requests.get(self._url, headers=self._headers)
        soup = bs(r.text, features='html.parser')
        topics = soup.find_all('a', {'class': a_topic_class})
        return [topic.text.strip() for topic in topics]
