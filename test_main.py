import pytest


@pytest.mark.parametrize("testinput,expected", [
    ('a', 'a')
])
def test(testinput, expected):
    return True
