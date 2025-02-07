from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', args=None)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            author=cls.author,
            slug='nazvanie'
        )
        cls.form_data = {'title': 'Название',
                         'slug': 'nazvanie', 'author': cls.author,
                         'text': 'Текст'}
        cls.note_url = reverse('notes:success', args=None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def setUp(self):
        self.response = self.auth_client.post(self.url, data=self.form_data)

    def test_anonymous_user_cant_create_note(self):
        initial_notes_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_notes_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.first()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.user)

    def test_two_same_slug(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.auth_client.post(self.url, data=self.form_data)
        warning = self.note.slug + WARNING
        notes_count_2 = Note.objects.count() - notes_count
        self.assertEqual(notes_count_2, 0)
        self.assertFormError(response, form='form',
                             field='slug', errors=warning)

    def test_automatic_creation_slug(self):
        Note.objects.all().delete()
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.first()
        max_slug_length = note._meta.get_field('slug').max_length
        expected_slug = slugify(self.note.title)[:max_slug_length]
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.note_url)
        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(slug=self.note.slug).exists())

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.note_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.form_data['author'])

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        note_from_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.slug, note_from_db.slug)
