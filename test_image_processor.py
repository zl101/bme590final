import pytest
from image_processor import *
from app import encode_image_as_b64_wmetrics

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()
    loginhist = fields.ListField()


@pytest.mark.parametrize("type , input, output", [
    (1, "./cat.jpg", "cathist.txt"),
    (0, np.array([1, 2]), "TypeError"),
    (0, np.array(['1', 2]), "TypeError")
])
def test_histogram_equalize(type, input, output):
    if type == 1:
        encoded = encode_image_as_b64_wmetrics(input)
        decodedim = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
        actual = histogram_equalize(decodedim)
        with open(output, "r") as file:
            expected = file.readline()
        file.close()
        assert actual == expected
    else:
        actual = histogram_equalize(input)
        assert actual == output


@pytest.mark.parametrize("type , input, output", [
    (1, "./cat.jpg", "catcon.txt"),
    (0, np.array([1, 2]), "TypeError"),
    (0, np.array(['1', 2]), "TypeError")
])
def test_contrast_stretch(type, input, output):
    if type == 1:
        encoded = encode_image_as_b64_wmetrics(input)
        decodedim = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
        actual = contrast_stretch(decodedim)
        with open(output, "r") as file:
            expected = file.readline()
        file.close()
        assert actual == expected
    else:
        actual = contrast_stretch(input)
        assert actual == output


@pytest.mark.parametrize("type , input, output", [
    (1, "./cat.jpg", "catlog.txt"),
    (0, np.array([1, 2]), "TypeError"),
    (0, np.array(['1', 2]), "TypeError")
])
def test_log_compress(type, input, output):
    if type == 1:
        encoded = encode_image_as_b64_wmetrics(input)
        decodedim = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
        actual = log_compress(decodedim)
        with open(output, "r") as file:
            expected = file.readline()
        file.close()
        assert actual == expected
    else:
        actual = log_compress(input)
        assert actual == output


@pytest.mark.parametrize("type , input, output", [
    (1, "./cat.jpg", "catgamma.txt"),
    (0, np.array([1, 2]), "TypeError"),
    (0, np.array(['1', 2]), "TypeError")
])
def test_gamma_correct(type, input, output):
    if type == 1:
        encoded = encode_image_as_b64_wmetrics(input)
        decodedim = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
        actual = gamma_correct(decodedim)
        with open(output, "r") as file:
            expected = file.readline()
        file.close()
        assert actual == expected
    else:
        actual = gamma_correct(input)
        assert actual == output


@pytest.mark.parametrize("type , input, output", [
    (1, "./cat.jpg", "catreverse.txt"),
    (0, np.array([1, 2]), "TypeError"),
    (0, np.array(['1', 2]), "TypeError")
])
def test_reverse_video(type, input, output):
    if type == 1:
        encoded = encode_image_as_b64_wmetrics(input)
        decodedim = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
        actual = reverse_video(decodedim)
        with open(output, "r") as file:
            expected = file.readline()
        file.close()
        assert actual == expected
    else:
        actual = reverse_video(input)
        assert actual == output


# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_validateNewUser(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_ValidateNewImage(args, expected, detected){
#
# }


@pytest.mark.parametrize("input, expected", [
    (np.array([1, 2, 3]), 1),
    ([1, 2, 3], 1),
    (np.array([1, 2, 3], dtype='uint8'), 0),
    (np.array([1, '2']), 1)
])
def test_validateRawImage(input, expected):
    assert validateRawImage(input) == expected


@pytest.mark.parametrize("input, expected", [
    ({"username": "wolf", "filename": "butterfly.jpg", "processing":
        "log_compress"}, 0),
    ({"username": "wolf", "processing": "log_compress"}, 1),
    ({"filename": "butterfly.jpg", "processing": "log_compress"}, 1),
    ({"username": "wolf", "filename": "butterfly.jpg"}, 1)
])
def test_validateInputs(input, expected):
    assert validateInputs(input) == expected
