import time

import requests

from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


class NewsSiteParser:
    """Класс, предназначенный для парсинга информации
    """

    def __init__(self, a_url):
        self._url = a_url
        self._user_agent = UserAgent()
        self._headers = {'accept': '*/*', 'user-agent': self._user_agent.safari}

    def get_news_topics(self, a_topic_class, a_time_sleep=1):
        """Функция парсинга топиков новостей

        :param a_topic_class: название класса объекта, который хранит информацию о топике
        :param a_time_sleep: время ожидания, если при считывании произошла ошибка
        :return: словарь типа {'название топика': 'href топика'}
        """

        topics = []
        while len(topics) == 0:
            r = requests.get(self._url, headers=self._headers)
            soup = bs(r.text, features='html.parser')
            topics = soup.find_all('a', {'class': a_topic_class})
            time.sleep(a_time_sleep)
        return {topic.text.strip(): topic.attrs['href'][4:] for topic in topics}

    def get_news(self, a_url_topic, a_shown_list=None, a_page=None, a_limit_preview_text=None,
                 a_additional_content_id=None):
        """Функция парсинга новостей

        :param a_url_topic: URL топика
        :param a_shown_list: список уже просмотренных новостей
        :param a_page: текущая страница просмотра новостей
        :param a_limit_preview_text: предельная длина считываемого контента новостей
        :param a_additional_content_id: идентификатор объекта, который представляет собой контент новостей
        :return: возвращает словарь, хранящий следующие параметры:
            id: идентификатор поста,
            url: URL новостей,
            title: название поста,
            text: контент поста
        """

        if a_shown_list is None:
            a_shown_list = []

        url = self._url + a_url_topic
        if a_page:
            url += f'page{a_page}/'

        news = {}

        r = requests.get(url, headers=self._headers)
        soup = bs(r.text, features='html.parser')
        articles = soup.find_all('article')

        article_id = None
        for article in articles:
            if int(article.attrs['id']) not in a_shown_list:
                article_id = article.attrs['id']
                break

        if article_id is None:
            return news

        news['id'] = article_id

        url = self._url + f'post/{article_id}/'
        news['url'] = url

        r = requests.get(url, headers=self._headers)
        soup = bs(r.text, features='html.parser')

        news['title'] = soup.find('h1').text
        news['text'] = ''

        text_blocks = soup.find_all('p')
        if len(text_blocks) < 2:
            if a_additional_content_id:
                content_block = soup.find_all('div', {'id': a_additional_content_id})
                text = content_block[0].text.strip()

                if a_limit_preview_text:
                    news['text'] = text[:a_limit_preview_text] + '...'
                else:
                    news['text'] = text
            else:
                news['text'] = 'При считывании данных поста произошла ошибка!'
        else:
            for block in text_blocks:
                if a_limit_preview_text:
                    if (len(news['text']) + len(block.text)) < a_limit_preview_text:
                        if len(news['text']) > 0:
                            news['text'] += '\n'
                        news['text'] += block.text
                    else:
                        if len(news['text']) > 0:
                            news['text'] += '\n'
                        news['text'] += block.text[:a_limit_preview_text - len(news['text'])]
                        news['text'] += '...'
                        break
                else:
                    news['text'] += block.text

        return news
