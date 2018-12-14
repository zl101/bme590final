import pytest
from app import detectFname, detectFilePathNoName, detectFtype, getRawName

p1 = "C:/a/b/cat.jpg"
p2 = "cat.jpg"
p3 = "C:/a/b/dog.png"


@pytest.mark.parametrize("testinput,expected", [
    (p1, "C:/a/b/"),
    (p2, -1),
    (p3, "C:/a/b/"),
])
def test(testinput, expected):
    res = detectFilePathNoName(testinput)
    assert res == expected
