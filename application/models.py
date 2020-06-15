import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Document):
    user_id     = db.IntField( unique=True )
    first_name  = db.StringField( max_length=50 )
    last_name   = db.StringField( max_length=50 )
    email       = db.StringField( max_length=30, unique=True )
    password    = db.StringField( )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)  

class Course(db.Document):
    courseID  = db.StringField( max_length=10, unique=True )
    title      = db.StringField( max_length=50 )
    description= db.StringField( max_length=255 )
    credits    = db.IntField()
    term       = db.StringField( max_length=25 )

class Enrollment(db.Document):
    user_id     = db.IntField ()
    courseID   = db.StringField( max_length=10 )

class newcustomer(db.Document):
    ssn_id         = db.IntField( unique=True )
    cust_id        = db.IntField ()
    name  = db.StringField( max_length=50 )
    age            = db.StringField( max_length=50 )
    address        = db.StringField( max_length=30 )
    state          =  db.StringField( max_length=20 )
    city           = db.StringField( max_length=15 )

# class UpdateUser(db.Document):
    
class UpdateCustomer(db.Document): ##########################
    def get_db(self):
        return self.db


   