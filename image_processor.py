from pymodm import connect
from pymodm import MongoModel, fields

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")

class Image(MongoModel):
    filename = fields.CharField(primary_key=True)
    raw_image = fields.CharField()
    processed_images = fields.DictField()
    metrics = fields.DictField()
    timestamp = fields.DateTimeField()


if __name__ == "__main__":
    img = Image(filename="img0",
                raw_image="5",
                processed_images = {},
                metrics ={})
    img.save()

    for i in Image.objects.raw({}):
        print(i)
        print(i.filename)
        print(i.processed_images)