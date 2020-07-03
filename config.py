import os


class Config(object):
    SECRET_KEY = os.environ.get(
        "SECRET_KEY") or b'jdncknzkcncomcozjvoksijvchcckcmm'
    MONGODB_SETTINGS = {
    'db': 'FlaskBank',
    'host': 'mongodb+srv://cluster-flaskbank.f042j.gcp.mongodb.net/FlaskBank?retryWrites=true&w=majority',
    'username':'mongoengine',
    'password':'SHIvam7426'
    }
