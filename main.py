"""
Парсер новостей. 932333 Цыбулаев Д.А.
"""


from bs4 import BeautifulSoup as BS
from datetime import datetime
from datetime import timedelta
import logging
import requests
import re
import time


URL = 'https://www.rbc.ru/short_news'
last_post_time = datetime.now() - timedelta(hours=2)

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def scrap_annotation_author_time(link):
    """
    Сбор аннотации, автора и времени
    """

    r = requests.get(link)
    s = BS(r.content, 'html.parser')

    if s.find('div', class_='article__text__overview'):
        annotation = s.find('div', class_='article__text__overview').text
    elif s.find('div', class_='article__text article__text_free'):
        annotation = s.find(
            'div', class_='article__text article__text_free').find_all('p')[0].text
    elif s.find('span', class_='MuiTypography-root MuiTypography-text quote-style-a93m3e'):
        annotation = s.find(
            'span', class_='MuiTypography-root MuiTypography-text quote-style-a93m3e').text
    else:
        annotation = 'Отсутствует'

    try:
        author = s.find('div', class_='article__authors__author__wrap').find(
            'span', class_='article__authors__author__name').text
    except AttributeError:
        author = 'Нет автора'

    if s.find('time', class_='article__header__date'):
        post_date = datetime.strptime(
            s.find('time', class_='article__header__date')['content']
            .split('+')[0], '%Y-%m-%dT%H:%M:%S')
    elif s.find('div', class_='MuiGrid-root MuiGrid-item quote-style-1wxaqej'):
        post_date = datetime.strptime(
            s.find('time')['datetime'].split('.')[0],
            '%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)

    return annotation, author, post_date


def search_posts(posts):
    """
    Поиск постов по ключевым словам
    """

    searched_posts = []

    for post in posts:
        a = post.find('a', class_='item__link rm-cm-item-link js-rm-central-column-item-link')
        header = post.find('span', class_='normal-wrap').text

        if re.search(r'Росс\w*', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        elif re.search(r'Кита\w*', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        elif re.search(r'США', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        elif re.search(r'санкц\w*', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        elif re.search(r'ЦБ\w*', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        elif re.search(r'Мосбирж\w*', header):
            link = a['href']
            annotation_author_time = scrap_annotation_author_time(link)
        else:
            continue

        annotation = annotation_author_time[0]
        author = annotation_author_time[1]
        post_date = annotation_author_time[2]
        log_post_date = post_date.strftime('%Y-%m-%d %H:%M:%S')
        theme = post.find('a', class_='item__category').text.split(',')[0]
        searched_posts.append([header, annotation, author,
                               post_date, theme, link])

        log = f"""
                Заголовок: {header}
                Аннотация: {annotation}
                Автор: {author}
                Время публикации: {log_post_date}
                Тема: {theme}
                Ссылка: {link}"""
        logging.info(log)

    return searched_posts


def check_last_post_time(post):
    """
    Проверка наличия новых постов
    """

    global last_post_time

    post_time_text = '2024-13-06 ' + post.find(
        'span', class_='item__category').text
    post_date = datetime.strptime(post_time_text, '%Y-%d-%m %H:%M')

    if post_date <= last_post_time:
        return 0, False
    return post_date, True


def get_posts():
    """
    Получаем новостную ленту
    """

    r = requests.get(URL)
    s = BS(r.content, 'html.parser')

    posts = s.find_all('div', class_='item__wrap l-col-center')
    post_date, check_date = check_last_post_time(posts[0])

    if not check_date:
        return False, False

    searched_posts = search_posts(posts)

    return post_date, searched_posts


if __name__ == '__main__':

    c = 0
    while c < 16:
        post_date, searched_posts = get_posts()

        # если есть новые посты, то меняем время последней публикации
        if post_date:
            last_post_time = post_date

        c += 1
        time.sleep(900)
