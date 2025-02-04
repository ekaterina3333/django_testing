from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Лев Простой')
        all_notes = [
            Note(title=f'Заметки {index}', text='Просто текст.',
                 author=cls.author,
                 slug=f'note-{index}')
            for index in range(1)
        ]
        Note.objects.bulk_create(all_notes)
        cls.note = Note.objects.create(
            title='Название',
            text='Просто текст.',
            author=cls.author
        )

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        first_note = object_list[0]
        self.assertIn(first_note, object_list)

    def test_notes_one_user(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
                self.assertIn('form', response.context)
