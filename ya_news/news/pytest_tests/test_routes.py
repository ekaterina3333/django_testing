import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.parametrize(
    'parametrized_client, expected_status, name, args',
    (
        (pytest.lazy_fixture('client'), HTTPStatus.OK, 'news:home', None),
        (pytest.lazy_fixture('client'), HTTPStatus.OK, 'users:login', None),
        (pytest.lazy_fixture('client'), HTTPStatus.OK, 'users:logout', None),
        (pytest.lazy_fixture('client'), HTTPStatus.OK, 'users:signup', None),
        (pytest.lazy_fixture('client'), HTTPStatus.OK, 'news:detail',
         pytest.lazy_fixture('news')),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         'news:delete', pytest.lazy_fixture('comment')),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND,
         'news:edit', pytest.lazy_fixture('comment')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK, 'news:delete',
         pytest.lazy_fixture('comment')),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK, 'news:edit',
         pytest.lazy_fixture('comment')),
    ),
)
def test_pages_availability(
    parametrized_client, expected_status, name, args, news, comment
):
    if name == 'news:detail':
        url = reverse(name, args=(args.id,))
    elif name == 'news:delete' or name == 'news:edit':
        url = reverse(name, args=(comment.id,))
    else:
        url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
