import pytest

from tests.helpers.auth_helpers import authenticated_as, make_supervisor_user


@pytest.fixture
def supervisor_user():
    return make_supervisor_user()


@pytest.fixture
def authenticated_supervisor(app, supervisor_user):
    with authenticated_as(app, supervisor_user):
        yield supervisor_user