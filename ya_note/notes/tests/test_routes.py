from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Лев Простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(title='Название', text='Текст',
                                        author=cls.author)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None, self.client, HTTPStatus.OK),
            ('users:login', None, self.client, HTTPStatus.OK),
            ('users:logout', None, self.client, HTTPStatus.OK),
            ('users:signup', None, self.client, HTTPStatus.OK),
            ('notes:list', None, self.author_client, HTTPStatus.OK),
            ('notes:success', None, self.author_client, HTTPStatus.OK),
            ('notes:add', None, self.author_client, HTTPStatus.OK),
            ('notes:edit', (self.notes.slug,), self.author_client,
             HTTPStatus.OK),
            ('notes:delete', (self.notes.slug,), self.author_client,
             HTTPStatus.OK),
            ('notes:detail', (self.notes.slug,), self.author_client,
             HTTPStatus.OK),
            ('notes:edit', (self.notes.slug,), self.reader_client,
             HTTPStatus.NOT_FOUND),
            ('notes:delete', (self.notes.slug,), self.reader_client,
             HTTPStatus.NOT_FOUND),
            ('notes:detail', (self.notes.slug,), self.reader_client,
             HTTPStatus.NOT_FOUND),
        )
        for address, args, client, status in urls:
            with self.subTest(address=address):
                url = reverse(address, args=args)
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
