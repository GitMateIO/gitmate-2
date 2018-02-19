import pytest


def pytest_addoption(parser):
    parser.addoption('--record-cassettes', action='store',
                     default='once', help='overwrites stored vcrpy cassettes')
    parser.addoption('--no-delete-unused', action='store_const', const=True,
                     default=False,
                     help='Disables deleting of unused interactions.')


@pytest.fixture(scope='class')
def vcrpy_record_mode(request):
    request.cls.vcrpy_record_mode = request.config.getoption(
        '--record-cassettes')


@pytest.fixture(scope='class')
def delete_unused_recordings(request):
    request.cls.delete_unused_recordings = not request.config.getoption(
        '--no-delete-unused')
