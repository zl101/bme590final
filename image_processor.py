import io
import base64
import datetime
import logging
import time
import math
import numpy as np
from pymodm import connect
from pymodm import MongoModel, fields
from flask import Flask, jsonify, request
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from skimage import data, exposure, img_as_float, util

app = Flask(__name__)

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()
    loginhist = fields.ListField()


def decode_b64_image_helper(base64_string, format, dimensions):
    decode = base64.b64decode(base64_string)
    res = np.frombuffer(decode, dtype=np.uint8)
    return np.reshape(res, dimensions)


def decode_image_fromb64(imstring, format, shape):
    imbytes = imstring.encode()
    decoded = decode_b64_image_helper(imbytes, format, shape)
    return decoded


def histogram_equalize(image):
    if (validateRawImage(image)):
        return "TypeError"
    nim = exposure.equalize_hist(image)
    nim = 255 * nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def contrast_stretch(image):
    if (validateRawImage(image)):
        return "TypeError"
    # min = np.amin(image)
    # max = np.amax(image)
    # con_str = lambda elem: (elem-min)*(((255-0)/(max-min))+0)
    # new_image = con_str(image)
    # new_image = 255*new_image
    # new_image = new_image.astype(np.uint8)
    nim = exposure.rescale_intensity(image, out_range=(0, 255))
    return base64.b64encode(nim).decode()


def log_compress(image):
    if (validateRawImage(image)):
        return "TypeError"
    # max = np.amax(image)
    # gain = float(255)/float(math.log(1+abs(max)))
    # log_com = lambda elem: gain*math.log(1+abs(elem))
    # new_image = log_com(image)
    # new_image = 255*new_image
    # new_image = new_image.astype(np.uint8)
    nim = exposure.adjust_log(image)
    nim = 255 * nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def reverse_video(image):
    if (validateRawImage(image)):
        return "TypeError"
    nim = util.invert(image)
    return base64.b64encode(nim).decode()


def gamma_correct(image):
    if (validateRawImage(image)):
        return "TypeError"
    nim = exposure.adjust_gamma(image, 0.5)
    nim = 255 * nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def validateRawImage(img_string):
    """
    checks that input is np.ndarray with dtype uint8
    :param img_string: string to be verified
    :return: 0 on success, 1 on fail
    """
    if (type(img_string).__module__ == np.__name__):
        if ('ndarray' in str(type(img_string))):
            if isinstance(img_string, np.ndarray):
                if str(img_string.dtype) == 'uint8':
                    return 0
    return 1


def validateInputs(dict):
    keys = ['username', 'processing', 'filename']
    for i in keys:
        if i not in dict.keys():
            return 1
    testcount = User.objects.raw({"_id": dict['username']}).count()
    if testcount == 0:
        return 2
    else:
        return 0


@app.route("/api/im_processing", methods=["POST"])
def process_image():
    # Histogram Equalization [default]
    # Contrast Stretching
    # Log Compression
    # Reverse Video
    """
    Needs filename, method, method_args, username
    """
    r = request.get_json()
    check = validateInputs(r)
    if check == 1:
        logging.eror("Insufficient information")
        return "KeyError"
    elif check == 2:
        logging.error("User does not exist")
        return "UserError"
    username = r['username']
    method = r['processing']
    usertoprocess = User.objects.raw({"_id": username}).first()
    for k in usertoprocess.imgslist:
        if k == "":
            continue
        if k['filename'] == r['filename']:
            whichim = k
            imstr = k['imgstring']
            image = decode_image_fromb64(imstr, k['filetype'], k['dimensions'])
            break
    start = time.time()
    if method.lower() == "histogram equalization":
        processed = histogram_equalize(image)
    elif method.lower() == "contrast stretching":
        processed = contrast_stretch(image)
    elif method.lower() == "log compression":
        processed = log_compress(image)
    elif method.lower() == "reverse video":
        processed = reverse_video(image)
    elif method.lower() == "gamma correction":
        processed = gamma_correct(image)
    else:
        return "no method found"
    if processed == "TypeError":
        logging.error("Image Invalid")
    end = time.time()
    elapsed_time = end - start
    if method.lower() in whichim["processeddict"]:
        data = whichim["processeddict"][method.lower()]
        times_run = data[3] + 1
    else:
        times_run = 1
    whichim["processeddict"][method.lower()] = [processed,
                                                datetime.datetime.now(),
                                                elapsed_time,
                                                times_run]
    usertoprocess.save()
    logging.info("Image Processing successful")
    return processed


if __name__ == "__main__":
    logging.basicConfig(filename="megatslog.txt",
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    app.run(host="127.0.0.1")
