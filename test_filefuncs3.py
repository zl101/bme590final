import pytest
from app import detectFname, detectFilePathNoName, detectFtype, getRawName

p1 = "C:/a/b/cat.jpg"
p2 = "cat.jpg"
p3 = "C:/a/b/dog.png"



@pytest.mark.parametrize("testinput,expected", [
    (p1, ".jpg"),
    (p2, ".jpg"),
    (p3, ".png"),
])
def test(testinput, expected):
    res = detectFtype(testinput)
    assert res == expected
