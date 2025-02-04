from datetime import timedelta as td

from django.utils import timezone as tz

import pytest

from news.constants import NEWS_COUNT_ON_HOME_PAGE
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def news_count_10(author):
    all_news = []
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.')
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Название',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def author_client(author, client):
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def commets(author, news):
    all_comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = tz.now() + td(days=index)
        comment.save()
        all_comments.append(comment)
    return all_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Лев Простой')
