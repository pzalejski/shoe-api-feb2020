from shoe_api import db, app, login_info
from werkzeug.security import generate_password_hash, check_password_hash

# import for flask-marhsmallow
from flask_marshmallow import Marshmallow

# import for flask_login Mixins
from flask_login.mixins import UserMixin

# instantiate marshmallow class
ma = Marshmallow(app)


# USER MODEL -- hold info for the user
@login_info.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(60), unique=True)  #want it to be completely different for every user that we have
    email = db.Column(db.String(50))
    password = db.Column(db.String(80))

    def __init__(self, public_id, email, password):
        self.public_id = public_id
        self.email = email
        self.password = self.password_has(password)


    def password_has(self, password):
        return generate_password_hash(password, salt_length=10)  #will hash and shift characters 10
        
# PRODUCT MODEL -- Hold info for the Shoe product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    desc = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)
    photo = db.Column(db.String(200))
    color = db.Column(db.String(50))

    def __init__(self, name, desc, price, qty, photo, color):
        self.name = name
        self.desc = desc
        self.price = price
        self.qty = qty
        self.photo = photo
        self.color = color


""" 
We will use Marshmallow (flask-marshmallow) to create a serialized version of our class. More plainly, we will create a flattened verison of our products class.

The end result will be come a schema by whicch we can create a basic string representation of our products  which will look like this:

{
    "id": 1,
    "name" : "Jordan 11",
    "price" : 299.99
    "description" : "Show worn in the last championship run"
    ...
    "photo" : "jumpman.jpg"
}
"""

class ProdcutSchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'desc', 'price', 'qty', 'photo', 'color')
        
product_schema = ProdcutSchema()
products_schema = ProdcutSchema(many=True)