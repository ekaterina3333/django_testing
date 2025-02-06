from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status, url',
    (
        (pytest.lazy_fixture('client'), HTTPStatus.OK, reverse('news:home')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK, reverse('users:login')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         reverse('users:logout')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         reverse('users:signup')),
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('detail_url')),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,
         pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK,
         pytest.lazy_fixture('edit_url')),
    ),
)
def test_pages_availability(
    parametrized_client, expected_status, url
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, url',
    (
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('client'), pytest.lazy_fixture('edit_url')),
    )
)
def test_redirects(parametrized_client, url):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = parametrized_client.get(url)
    assertRedirects(response, expected_url)
