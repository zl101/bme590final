from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget,QPushButton,QAction,QLineEdit,QMessageBox, QFileDialog, QComboBox
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import numpy as np
import io
import base64
import datetime
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from pymodm import connect
from pymodm import MongoModel, fields

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


def detectFname(path):
    loc = path.rfind("/")
    if(loc == -1):
        return path
    else:
        return path[loc+1:]


def detectFtype(path):
    loc = path.rfind(".")
    if(loc == -1):
        print("youre fucked")
        return loc
    else:
        return path[loc:]


def constructImg(uploadTime, fileName, imgString, fileType, dimensions):
    toret = {}
    toret['uploadtime'] = uploadTime
    toret['filename'] = fileName
    toret['imgstring'] = imgString
    toret['processeddict'] = {}
    toret['filetype'] = fileType
    toret["dimensions"] = dimensions
    return toret


def encode_image_as_b64_wmetrics(image_path):
    imname = detectFname(image_path)
    img = np.asarray(Image.open(image_path))
    shape = img.shape
    imtype = detectFtype(image_path)
    return [imname, imtype, shape, base64.b64encode(img).decode()]


def decode_b64_image_helper(base64_string, format, dimensions):
    decode = base64.b64decode(base64_string)
    res = np.frombuffer(decode, dtype=np.uint8)
    return np.reshape(res, dimensions)


def decode_image_fromb64(imstring, format, shape):
    imbytes = imstring.encode()
    decoded = decode_b64_image_helper(imbytes, format, shape)
    return decoded


def validateNewUser(input):
    """
    -1 for invalid, 0 for already exists, 1 for ur gucci
    """
    checkUserExist = User.objects.raw({"_id": input}).count()
    if(checkUserExist == 0):
        return 1
    else:
        return 0


def upload_image(user, filename, filetype, dimensions, filedata):
    """
    Needs fields filename, filedata, username, filetype, dimensions
    """
    # img = Image(datetime.datetime.now(),
    #             r['filename'],
    #             r['filedata'])
    newim = constructImg(datetime.datetime.now(),
                        filename,
                        filedata,
                        filetype,
                        dimensions)
    # if len(User.objects.({"_id": user}))==0:
    #    createUser(user)
    user_call = User.objects.raw({"_id": user}).first()
    user_call.imgslist.append(newim)
    user_call.save()
    return 1


def showIM(username, filename):
    user_call = User.objects.raw({"_id": username}).first()
    for k in user_call.imgslist:
        if k == "":
            continue
        if k['filename'] == filename:
            #imdata = k['imgstring']
            decodedim = decode_image_fromb64(k['imgstring'], k['filetype'], k['dimensions'])
    plt.imshow(decodedim)
    plt.show()


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title='Hello, world!'
        self.left=290
        self.top=200
        self.width=800
        self.height=800
        self.files = []
        self.user = ""
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.textbox=QLineEdit(self)
        self.textbox.move(30,30)
        self.textbox.setText("Username")
        self.textbox2=QLineEdit(self)
        self.textbox2.move(30,100)
        self.textbox.resize(280,40)
        self.textbox2.resize(280,40)
        self.textbox3=QLineEdit(self)
        self.textbox3.move(30,200)
        self.textbox3.setText("Username")
        self.textbox3.resize(280,40)
        self.button=QPushButton('Set or Create User',self)
        self.button.move(30,600)
        self.button.clicked.connect(self.callCreateUser)
        self.button2=QPushButton('Add Image',self)
        self.button2.move(180,600)
        self.button2.clicked.connect(self.callAddImage)
        self.button3=QPushButton('Upload Added Images',self)
        self.button3.move(330,600)
        self.button3.clicked.connect(self.callProcessImages)
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("A")
        self.comboBox.addItem("B")
        self.comboBox.addItem("C")
        self.comboBox.addItem("D")
        self.comboBox.move(480, 400)
        self.button4=QPushButton('Do IM Processing',self)
        self.button4.move(480,600)
        self.button4.clicked.connect(self.callExternalProcessing)
        self.button5=QPushButton('Show Image',self)
        self.button5.move(630,600)
        self.button5.clicked.connect(self.showImage)
        self.button5=QPushButton('Test',self)
        self.button5.move(300,350)
        self.button5.clicked.connect(self.on_click)
        #self.imlabel = Qlabel(self)

        self.show()
      # @pyqtSlot()
    def callCreateUser(self):
        username = self.textbox.text()
        check = validateNewUser(username)
        msg = ""
        if(check == -1):
           msg = "Invalid"
        if(check == 0):
           msg =  "User Set (Already Exists)"
           self.user = username
        if check==1:
            u = User(username=username, imgslist=[""])
            u.save()
            msg =  "User Created"
        QMessageBox.question(self, 'Hello, world!',msg, QMessageBox.Ok, QMessageBox.Ok)

    def callAddImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath() , '*.jpg;*.png;*.tiff')
        self.files.append(fileName)
        QMessageBox.question(self, 'Message!', "Image Added to List",QMessageBox.Ok, QMessageBox.Ok)

    def callProcessImages(self):
        for filepath in self.files:
            temp = encode_image_as_b64_wmetrics(filepath)
            upload_image(self.user, temp[0], temp[1], temp[2], temp[3])

    def showImage(self):
        showIM(self.user, self.textbox2.text())
        #r= requests.post("http://127.0.0.1:5000/api/upload_image", json={"username":"chris", "filename":fname})

    def callExternalProcessing(self):
        print(self.comboBox.currentText())
        #r= requests.post("http://127.0.0.1:5000/api/improcessing", json={"username":"chris", "filename":"cat.jpg", "processing": "histogram equalization"})

    def on_click(self):
        #textboxValue=self.textbox.text()
        #QMessageBox.question(self, 'Hello, world!', "Confirm: "+textboxValue,QMessageBox.Ok, QMessageBox.Ok)
        ret = QFileDialog.getOpenFileNames(self, 'Single File', QtCore.QDir.rootPath() , '*.jpg;*.png;*.tiff')
        #QMessageBox.question(self, 'Hello, world!', "Confirm: "+fileName,QMessageBox.Ok, QMessageBox.Ok)
        print(ret)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    ex=App()
    sys.exit(app.exec_())
