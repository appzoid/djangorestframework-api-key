import pytest
from django.conf import settings


def pytest_configure():
    settings.configure(
        **dict(
            SECRET_KEY="abcd",
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.sessions",
                "django.contrib.contenttypes",
                "rest_framework",
                "rest_framework_api_key",
            ],
            ROOT_URL_CONF="urls",
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
        )
    )


@pytest.fixture
def view_with_permissions():
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.response import Response

    def create_view(*classes):
        @api_view()
        @permission_classes(classes)
        def view(*args):
            return Response()

    return create_view


def _create_user():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(username="foo", password="bar")


@pytest.fixture
def create_api_key():
    from .factory import create_api_key as factory

    return factory


@pytest.fixture
def create_request():
    from rest_framework.test import APIRequestFactory, force_authenticate
    from rest_framework_api_key.settings import TOKEN_HEADER, SECRET_KEY_HEADER

    factory = APIRequestFactory()

    def create(token=None, secret_key=None, authenticated=False):
        kwargs = {}

        if token is not None:
            kwargs[TOKEN_HEADER] = token

        if secret_key is not None:
            kwargs[SECRET_KEY_HEADER] = secret_key

        request = factory.get("/test/", **kwargs)

        if authenticated:
            user = _create_user()
            force_authenticate(request, user=user)

        return request

    return create
