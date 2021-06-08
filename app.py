from flask import Flask, render_template, request, json, redirect, flash
from flask import session, url_for
from passlib.hash import sha256_crypt
from pymongo import MongoClient

import uuid
import math
import re

app = Flask(__name__)

client = MongoClient()
db = client.web_store
Users = db.User
Inventory = db.Inventory
Cart = db.Cart

brands = ['Hunter', 'Rain Bird', 'Weathermatic']
products = ['Controllers', 'Sprinklers', 'Valves', 'Rotors']

# Login routing and sign-in and sign-up logic

app.secret_key = 'cs6314.0w1'
@app.route('/')
def main():
    inventory = [item for item in Inventory.find()]
    sprinklers_showcase = [item for item in inventory if item['category'] == 'sprinkler-body' or item['category'] == 'sprinkler-nozzles']
    valves_showcase = [item for item in inventory if item['category'] == 'valves']
    controllers_showcase = [item for item in inventory if item['category'] == 'controller']
    rotors_showcase = [item for item in inventory if item['category'] == 'rotors']
    
    return render_template('index.html', sprinklers=sprinklers_showcase[:4], rotors=rotors_showcase[:4], valves=valves_showcase[:4], controllers=controllers_showcase[:4], brands=brands, products=products)

@app.route('/userLanding')
def showUserLanding():
    try:
        if session.get('user'):
            data = Users.find_one({'_id': session.get('user')})
            if data:
                if data['isAdmin'] == '1':
                    return redirect('/admin')
                else:
                    return render_template('userLanding.html', data=data)
        else:
            return render_template('error.html', error="Unauthorized Access")
    except Exception as e:
        return render_template('error.html', error=str(e), data=data)

@app.route('/cart', methods=['POST', 'GET'])
def shopping_cart():
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        return render_template('cart.html', data=data)
    else:
        flash('Please sign in to have access to your cart.')
        return redirect('/showSignIn')

@app.route("/addToCart", methods=['POST', 'GET'])
def addToCart():
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        item_to_add = request.args.get('productId')
        product = Inventory.find_one(item_to_add)
        if product != None:
            product.update({'user_id': user_data['_id']})
            Cart.insert_one(product)
        return redirect('/')
    else:
        flash("Please log in to access your cart.")
        return redirect("/showSignIn")

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        data = Users.find_one({"email": _email})
        if data:
            # if data['password'] == _password:
            if sha256_crypt.verify(_password, data['password']):
                session['user'] = data['_id']
                if data['isAdmin'] == "1":
                    return "admin"
                else:
                    return "user"
            else:
                return "Wrong email address or password."
        else:
            return "Wrong email address or password."
    except Exception as e:
        return render_template('error.html', error=str(e), data=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp', methods=['POST'])
def signUp():
    # Read the posted values from the UI
    _fname = request.form['inputFname']
    _lname = request.form['inputLname']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _confirmpswd = request.form['confirmPassword']
    _regex = '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}'

    # Validate the received values
    if _fname and _lname and _email and _password and _confirmpswd:

        # Check if the email address is already in the database.
        # returns 1 if the email is already registered
        if len(_email) != 0:
            data = Users.find_one({"email": _email})
            if data:
                return "User already exists."

        # Check if password matches password requirements
        # otherwise, display to the user password requirements.
        if re.match(_regex, _password):
            # Check if password matches password confirmation
            # If it does, insert it to the database and create a new user.
            # Otherwise display password does not match error.
            if _password == _confirmpswd:
                _password = sha256_crypt.hash(_password)
                new_user = {
                    '_id': str(uuid.uuid1()),
                    'fname': _fname,
                    'lname': _lname,
                    'email': _email,
                    'password': _password,
                    'isAdmin': "0"
                }
                Users.insert_one(new_user)
                return "User created successfully."
            else:
                return "Passwords do not match."
        else:
            return "Password requirements:\n* at least one number\n* at least one uppercase letter\n* at least one lowercase letter\n* must be at least 8 or more characters."
    else:
        return "Please enter the required fields."

# End log-in and sign-up logic and routing

# CRUD for admin page
# List all inventory
@app.route('/admin', methods=['GET', 'POST'])
def showAdminDashboard():
   
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        inventory_data = [item for item in Inventory.find()]

        if user_data:
            if user_data['isAdmin'] == '1':
                return render_template('admin.html', data=user_data, inventory=inventory_data)
            else:
                return render_template('error.html', error='Unauthorized Access', data=user_data)
    else:
        return render_template('error.html', error="Unauthorized Access")


# delete - soft delete item
@app.route('/admin/delete/<id>', methods=['GET', 'POST'])
def deleteItem(id):

    if session.get('user'):
        query = {'_id': id}
        isDeleted = { '$set': {'isDeleted': True}}
        Inventory.update_one(query, isDeleted)
        flash('Item deleted.')
        return redirect('/admin')
    else:
        return render_template('error.html', error="Unauthorized Access")
            

# update
@app.route('/admin/update/<id>', methods=['GET', 'POST'])
def updateItem(id):

    updated = {'Product Name': '', 'Product Price': '', 'Product Stock': '', 'Product Image': '', 'message': ''}

    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        query = {'_id': id}
        inventory_item = Inventory.find_one(query)
        if request.method == 'POST':
            _productName = request.form['product-name']
            _productPrice = request.form['product-price']
            _productStock = request.form['product-stock']
            _productImage = request.form['product-image']
            if _productName:
                new_name = {'$set': {'productName': _productName}}
                Inventory.update_one(query, new_name)
                updated['Product Name'] = _productName
                updated['message'] = 'updated'
            if _productPrice:
                new_price = {'$set': {'price': float(_productPrice)}}
                Inventory.update_one(query, new_price)
                updated['Product Price'] = _productPrice
                updated['message'] = 'updated'

            if _productStock:
                new_stock = {'$set': {'stock': int(_productStock)}}
                Inventory.update_one(query, new_stock)
                updated['Product Stock'] = _productStock
                updated['message'] = 'updated'

            if _productImage:
                new_image = {'$set': {'imageUrl': _productImage}}
                Inventory.update_one(query, new_image)
                updated['Product Image'] = _productImage
                updated['message'] = 'updated'

        return render_template('updateItem.html', data=user_data, inventory_item=inventory_item, updated = updated)
    else:
        return render_template('error.html', error="Unauthorized Access")



# Create - new inventory
@app.route('/admin/create', methods=['GET', 'POST'])
def createItem():
    brands = [{'name': 'hunter'}, {'name': 'rainbird'}, {'name': 'weathermatic'}]
    category = [{'name': 'controller'}, {'name': 'rotors'}, {'name': 'sprinkler-body'}, {'name': 'sprinkler-nozzles'}, {'name': 'valves'}]
    inserted = ''
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        if request.method == 'POST':
            try:
                _productName = request.form['product-name']
                _productPrice = request.form['product-price']
                _productCategory = request.form['product-category']
                _productBrand = request.form['product-brand']
                _productStock = request.form['product-stock']
                _productImage = request.form['product-image']
                # Create new item to database
                if _productName and _productPrice and _productCategory and _productBrand and _productStock and _productImage:
                    new_item = {
                        '_id': str(uuid.uuid1()),
                        'productName': _productName,
                        'price': float(_productPrice),
                        'category': _productCategory.lower(),
                        'brand': _productBrand.lower(),
                        'stock': int(_productStock),
                        'imageUrl': 'static/img/'+_productBrand.lower()+'/'+_productCategory.lower()+'/'+_productImage
                    }
                    Inventory.insert_one(new_item)
                    inserted = 'true'
                    # Item was inserted successfully.
                else:
                    #  All fields must be filled out.
                    inserted = 'false'

            except Exception as e:
                return str(e)

        if user_data:
            if user_data['isAdmin'] == '1':
                return render_template('createItem.html', data=user_data, brands=brands, category=category, response=inserted) 
            else:
                return render_template('error.html', error='Unauthorized Access', data=user_data)
    else:
        return render_template('error.html', error="Unauthorized Access")




if __name__ == '__main__':
    app.run()