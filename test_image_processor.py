import pytest
from image_processor import *

#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_ecode_b64_image_helper(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_decode_image_from_b64(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_contrast_stretch(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_log_compress(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_reverse_video(args, expected, detected){
#
# }
#
#
# @pytest.mark.parametrize("filename, expected, detected", [
# ])
# def test_gamma_correct(args, expected, detected){
#
# }
#
#
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
    (np.array([1, 2, 3], dtype = 'uint8'),0),
    (np.array([1, '2']),1)
])
def test_validateRawImage(input, expected):
    assert validateRawImage(input) == expected