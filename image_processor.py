import io
import base64
import datetime
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


def decode_b64_image_helper(base64_string, format, dimensions):
    decode = base64.b64decode(base64_string)
    res = np.frombuffer(decode, dtype=np.uint8)
    return np.reshape(res, dimensions)


def decode_image_fromb64(imstring, format, shape):
    imbytes = imstring.encode()
    decoded = decode_b64_image_helper(imbytes, format, shape)
    return decoded


def histogram_equalize(image):
    nim = exposure.equalize_hist(image)
    nim = 255*nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def contrast_stretch(image):
    # min = np.amin(image)
    # max = np.amax(image)
    # con_str = lambda elem: (elem-min)*(((255-0)/(max-min))+0)
    # new_image = con_str(image)
    # new_image = 255*new_image
    # new_image = new_image.astype(np.uint8)
    nim = exposure.rescale_intensity(image,out_range=(0,255))
    return base64.b64encode(nim).decode()


def log_compress(image):
    # max = np.amax(image)
    # gain = float(255)/float(math.log(1+abs(max)))
    # log_com = lambda elem: gain*math.log(1+abs(elem))
    # new_image = log_com(image)
    # new_image = 255*new_image
    # new_image = new_image.astype(np.uint8)
    nim = exposure.adjust_log(image)
    nim = 255*nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def reverse_video(image):
    nim = util.invert(image)
    return base64.b64encode(nim).decode()


def gamma_correct(image):
    nim = exposure.adjust_gamma(image, 0.5)
    nim = 255*nim
    nim = nim.astype(np.uint8)
    return base64.b64encode(nim).decode()


def validateNewUser(input):
    """
    -1 for invalid, 0 for already exists, 1 for ur gucci
    """
    if(not isinstance(input, type({}))):
        return -1
    if "username" not in input.keys():
        return -1
    if(not isinstance(input["username"], type("a"))):
        return -1
    checkUserExist = User.objects.raw({"_id": input['username']}).count()
    if(checkUserExist == 0):
        return 1
    else:
        return 0


def validateNewImage(input):
    if(not isinstance(input, type({}))):
        return -1
    if "username" not in input.keys():
        return -1
    if "filename" not in input.keys():
        return -1
    if "filetype" not in input.keys():
        return -1
    if "filedata" not in input.keys():
        return -1
    if "dimensions" not in input.keys():
        return -1
    return 1



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
    username = r['username']
    method = r['processing']
    # validate json, parse json
    usertoprocess = User.objects.raw({"_id": username}).first()
    for k in usertoprocess.imgslist:
        if k == "":
            continue
        if k['filename'] == r['filename']:
            whichim = k
            imstr = k['imgstring']
            image = decode_image_fromb64(imstr, k['filetype'], k['dimensions'])
            break
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
    whichim["processeddict"][method.lower()] = [processed
                                                ,datetime.datetime.now()]
    usertoprocess.save()
    return processed


if __name__ == "__main__":
    app.run(host="127.0.0.1")