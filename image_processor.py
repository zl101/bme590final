import io
import base64
import datetime
import numpy as np
from pymodm import connect
from pymodm import MongoModel, fields
from flask import Flask, jsonify, request
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

app = Flask(__name__)

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()

# class Image():
#     def __init__(self, uploadTime, fileName, imgString):
#         self.uploadtime = uploadTime
#         self.filename = fileName
#         self.imgstring = imgString
#         self.processedDict = {}


def constructImg(uploadTime, fileName, imgString, fileType, dimensions):
    toret = {}
    toret['uploadtime'] = uploadTime
    toret['filename'] = fileName
    toret['imgstring'] = imgString
    toret['processeddict'] = {}
    toret['filetype'] = fileType
    toret["dimensions"] = dimensions
    return toret

# class Image(MongoModel):
#     uploadtime = fields.
#     filename = fileName
#     imgstring = imgString
#     processedDict = {}


def encode_image_as_b64(image_path):
    img = np.asarray(Image.open(image_path))
    return base64.b64encode(img)


def encode_image_nopath(image):
    return base64.b64encode(image)


def decode_b64_image(base64_string, format, dimensions):
    decode = base64.b64decode(base64_string)
    res = numpy.frombuffer(decode, dtype=numpy.uint8)
    return numpy.reshape(res, dimensions)


def histogram_equalize(image):
    nim = exposure.equalize_hist(image)
    nim = 256*nim
    nim = nim.astype(np.uint8)
    return encode_image_no_path(nim)


def contrast_stretch(image, args):
    return 0


def log_compress(image, args):
    return 0


def reverse_video(image, args):
    return 0


def validateNewUser(input):
    return True


def validateNewImage(input):
    return True


@app.route("/api/create_user", methods=["POST"])
def createUser():
    r = request.get_json()
    username = r['username']
    if(validateNewUser(r) == -1):
        return "not valid user"
    u = User(username=username, imgslist=[""])
    u.save()
    return "success"


@app.route("/api/upload_image", methods=["POST"])
def upload_image():
    """
    Needs fields filename, filedata, username, filetype, dimensions
    """
    r = request.get_json()
    if(validateNewImage(r) == -1):
        return "not valid user"
    # img = Image(datetime.datetime.now(),
    #             r['filename'],
    #             r['filedata'])
    user = r['username']
    newim = constructImg(datetime.datetime.now(),
                         r['filename'],
                         r['filedata'],
                         r['filetype'],
                         r["dimensions"])
    # if len(User.objects.({"_id": user}))==0:
    #    createUser(user)
    user_call = User.objects.raw({"_id": user}).first()
    user_call.imgslist.append(newim)
    user_call.save()
    return "success"


@app.route("/api/process_image/", methods=["POST"])
def process_image():
    # Histogram Equalization [default]
    # Contrast Stretching
    # Log Compression
    # Reverse Video
    """
    Needs filename, method, method_args, username
    """
    r = request.get_json()
    usertoprocess = User.objects.raw({"_id": username}).first()
    for k in usertoprocess.imgslist:
        if k == "":
            continue
        if k['filename'] == r['filename']:
            whichim = k
            imstr = k['imstring']
            image = decode_b64_image(imstr, k['filetype'], k['dimensions'])
            break
    # raw_img = image_to_process.raw_image
    if method.lower() == "histogram equalization":
        processed = histogram_equalize(image)
    elif method.lower() == "contrast stretching":
        processed = contrast_stretch(raw_img, method_args)
    elif method.lower() == "log compression":
        processed = log_compress(raw_img, method_args)
    elif method.lower() == "reverse video":
        processed = reverse_video(raw_img, method_args)
    else:
        return -1
    whichim["processeddict"][method.lower()] = [processed,
                                                datetime.datetime.now()]
    usertoprocess.save()


if __name__ == "__main__":
    app.run(host="127.0.0.1")
    # img = Image(filename="img0",
    #             raw_image="5",
    #             processed_images = {},
    #             metrics ={})
    # img.save()
    #
    # for i in Image.objects.raw({}):
    #     print(i)
    #     print(i.filename)
    #     print(i.processed_images)

    # filepath = "./cat.jpg"
    # encoded = encode_image_as_b64(filepath)
    # print(encoded)
    # decode_b64_image(encoded)
    # r2 = requests.post("http://bme590.suyash.io/sum", json={"a": 1, "b": 2})
