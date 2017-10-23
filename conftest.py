import pytest


def pytest_addoption(parser):
    parser.addoption('--record-cassettes', action='store',
                     default='once', help='overwrites stored vcrpy cassettes')


@pytest.fixture(scope='class')
def vcrpy_record_mode(request):
    request.cls.vcrpy_record_mode = request.config.getoption(
        '--record-cassettes')
