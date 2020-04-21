from shoe_api import app, db
from shoe_api.models import User, Product, check_password_hash, product_schema, products_schema
from flask import render_template, request, redirect, url_for, jsonify

from shoe_api.forms import UserForm, LoginForm
from flask_login import login_user, current_user, login_required

import uuid

# imports for API token (api key)
import jwt
import datetime

from functools import wraps

# create user route
@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    form = UserForm()

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        # creates a univerally unique identifier string
        public_id = str(uuid.uuid4())
        print(email, password, public_id)
        
        #add all info to db
        user = User(public_id, email, password)
        
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    else:
        print('Form is not valid')
    return render_template('sign_up.html',form=form)


# create login route
@app.route('/login', methods=['GET', 'POST'])
def login():

    loginForm = LoginForm()
    if request.method == 'POST' and loginForm.validate():
        email = loginForm.email.data
        password = loginForm.password.data
        logged_user = User.query.filter(User.email == email).first()
        print(f'login-info: {email}, {password}, {logged_user.password}')
        if logged_user and check_password_hash(logged_user.password,password):#checks pw from db and the one put in on the form
            login_user(logged_user)
            print(f'current User public_id {current_user.public_id}')
        else:
            print('invalid credentials')
            return redirect(url_for('login'))
        return redirect(url_for('get_api'))
    return render_template('login.html',form=loginForm)

# get API KEY route
@app.route('/getapi', methods=['GET'])
def get_api():
    if current_user:
        print(current_user.public_id)
        #identify who you are based on database
        #when it will expire
        #uses key to generate token
        token = jwt.encode({'public_id': current_user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({"token":token.decode('UTF-8')})

# customer decorator to create and validate API KEY
def token_required(our_flask_function):
    # all token_required is doing is checking if we have current_user_token in our_flask_function()
    @wraps(our_flask_function)  #copy the contnets of the returned function, specifically the parameters
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user_token = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return our_flask_function(current_user_token, *args, **kwargs)
    
    return decorated

@app.route('/product', methods=['POST'])
@token_required
def add_product(current_user_token):
    #when adding to the database
    name = request.json['name']
    desc = request.json['desc']
    price = request.json['price']
    qty = request.json['qty']
    photo = request.json['photo']
    color = request.json['color']

    new_product = Product(name, desc, price, qty, photo, color)
    
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


#get one product
@app.route('/product/<id>', methods=['GET'])
@token_required
def get_product(current_user_token, id):  #token_required tells get_productwhat params it needs
    product = Product.query.get(id)
    return product_schema.jsonify(product)


#get all product
@app.route('/product', methods=['GET'])
@token_required
def getall_products(current_user_token):  #token_required tells get_productwhat params it needs
    products = Product.query.all()
    result = products_schema.dump(products)
    return jsonify(result)


# update product route (endpoint)
@app.route('/product/<id>', methods=['PUT'])
@token_required
def update_product(current_user_token):
    product = Product.quert.get(id)

    name = request.json['name']
    desc = request.json['desc']
    price = request.json['price']
    qty = request.json['qty']
    photo = request.json['photo']
    color = request.json['color']

    #updates to the database from the request that came in
    product.name = name
    prodcut.desc = desc
    product.price = price
    product.qty = qty
    product.photo = photo
    product.color = color

    #commit to db
    db.session.commit()

    return product_schema.jsonify(product)


# delete route (aka delete endpoint)
@app.route('/product/<id>', methods=['DELETE'])
@token_required
def delete_product(current_user_token):
    #look for the product to delete via the id
    product = Product.query.get(id)

    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)