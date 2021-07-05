from flask import Flask, render_template, request, json, redirect, flash
from flask import session, url_for
from passlib.hash import sha256_crypt
from pymongo import MongoClient
from itsdangerous import URLSafeSerializer

import uuid
import math
import datetime
import re
from decimal import Decimal

app = Flask(__name__)

client = MongoClient()
db = client.web_store
Users = db.User
Inventory = db.Inventory
Cart = db.Cart
Order_History = db.OrderHistory
Resets = db.Resets
inventory = [item for item in Inventory.find()]
brands = {item['brand'] for item in inventory}
products = {item['category'] for item in inventory}

app.secret_key = uuid.uuid4().hex

@app.route("/")
def main():
    user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
    # Get cart quantity to display in navbar badge
    cart_quantity = 0
    for item in user_cart:
        cart_quantity += Decimal(str(item['quantity']))
    return render_template('index.html', cart_quantity=cart_quantity, products=products)

# @app.route('/')
# def OLD_index():
#     sprinklers_showcase = [item for item in inventory if item['category'] == 'Sprinklers' or item['category'] == 'Nozzles']
#     valves_showcase = [item for item in inventory if item['category'] == 'Valves']
#     controllers_showcase = [item for item in inventory if item['category'] == 'Controllers']
#     rotors_showcase = [item for item in inventory if item['category'] == 'Rotors']

#     user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
#     # Get cart quantity to display in navbar badge
#     cart_quantity = 0
#     for item in user_cart:
#         cart_quantity += Decimal(str(item['quantity']))
    
#     return render_template('index.html', sprinklers=sprinklers_showcase[:4], rotors=rotors_showcase[:4], valves=valves_showcase[:4], controllers=controllers_showcase[:4], brands=brands, products=products, cart_quantity=cart_quantity)

''' ***** Routes for product display pages *****

Each category type it's own template.
Each page will display appropriate items based on category.
Each item will show product description, price, stock, image, quantity modifier and a 'add to cart' button.

'''

@app.route('/products/sprinklers')
def Sprinklers():
    inventory = [item for item in Inventory.find()]
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        sprinkler_products = [product for product in inventory if product['category'] == 'Sprinklers']
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('products/sprinkler-body.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products, inventory=sprinkler_products)
    else:
        sprinkler_products = [product for product in inventory if product['category'] == 'Sprinklers']
        return render_template('products/sprinkler-body.html', brands=brands, products=products, inventory=sprinkler_products)

@app.route('/products/rotors')
def Rotors():
    inventory = [item for item in Inventory.find()]
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        rotor_products = [product for product in inventory if product['category'] == 'Rotors']
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('products/rotors.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products, inventory=rotor_products)
    else:
        rotor_products = [product for product in inventory if product['category'] == 'Rotors']
        return render_template('products/rotors.html', brands=brands, products=products, inventory=rotor_products)
    
@app.route('/products/controllers')
def Controllers():
    inventory = [item for item in Inventory.find()]
    if session.get('user'):
        controller_products = [product for product in inventory if product['category'] == 'Controllers']
        data = Users.find_one({'_id': session.get('user')})
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('products/controllers.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products, inventory=controller_products)
    else:
        controller_products = [product for product in inventory if product['category'] == 'Controllers']
        return render_template('products/controllers.html', brands=brands, products=products, inventory=controller_products)
@app.route('/products/valves')
def Valves():
    inventory = [item for item in Inventory.find()]
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        valve_products = [product for product in inventory if product['category'] == 'Valves']
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('products/valves.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products, inventory=valve_products)
    else:
        valve_products = [product for product in inventory if product['category'] == 'Valves']
        return render_template('products/valves.html', brands=brands, products=products, inventory=valve_products )

@app.route('/products/nozzles')
def Nozzles():
    inventory = [item for item in Inventory.find()]
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        nozzle_products = [product for product in inventory if product['category'] == 'Nozzles']
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('products/sprinkler-nozzles.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products, inventory=nozzle_products)
    else:
        nozzle_products = [product for product in inventory if product['category'] == 'Nozzles']
        return render_template('products/sprinkler-nozzles.html', brands=brands, products=products, inventory=nozzle_products)

''' ***** End routes for product display pages ***** '''

'''
Password reset screen:
Displays screen if user clicks on 'forgot password' on sign in template
'''
@app.route('/login/reset')
def resetPasswordForm():
    return render_template('resetPassword.html', brands=brands, products=products)

'''
Password reset 
- Check if email provided exists
- generates random hash as a key, stores it, its current timestamp and user id to db and sends it to the user

When user apply secret key (for example with url or special form) you should:
validate it (exist, not expired, not used before)
get user identifier
delete or mark as used current secret key
provide logic to enter/generate new password.

TODO:
Do not know how to send email.
'''

@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():

    _email = request.form['inputEmail']
    try:
        data = Users.find_one({"email": _email})
        if data:
            random_hash = str(uuid.uuid4())
            secret_key = sha256_crypt.hash(random_hash)
            timestamp = str(datetime.datetime.now())
            user_id = data['_id']
            reset_info = {
                'secret_key': secret_key,
                'timestamp': timestamp,
                'user_id': user_id,
                'reset': False,
            }
            Resets.insert_one(reset_info)
            return "A password reset link will be sent to this email address if the email address is associated with an account."
        else:
            return "A password reset link will be sent to this email address if the email address is associated with an account. Does not Exists."
    except Exception as e:
        return str(e)
    return _email

''' ***** Profile edits ***** '''

'''
User landing screen:
Will display a hello message and available actions on the side bar
'''
@app.route('/user/profile')
def showUserLanding():
    try:
        if session.get('user'):
            data = Users.find_one({'_id': session.get('user')})
            if data:
                if data['isAdmin'] == '1':
                    return redirect('/admin')
                else:
                    user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
                    # Get cart quantity to display in navbar badge
                    cart_quantity = 0
                    for item in user_cart:
                        cart_quantity += Decimal(str(item['quantity']))

                    return render_template('/profile/userLanding.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products)

        else:
            return render_template('error.html', error="Unauthorized Access", products=products)
    except Exception as e:
        return render_template('error.html', error=str(e), data=data)

'''
Profile update screen:
Displays forms to update email address or password.
'''
@app.route('/user/profile/update')
def updateProfile():
    try:
        if session.get('user'):
            data = Users.find_one({'_id': session.get('user')})
            user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
            cart_quantity = 0
            for item in user_cart:
                cart_quantity += Decimal(str(item['quantity']))
            return render_template('/profile/updateProfile.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products)
        else:
            return render_template('error.html', error="Unauthorized Access", products=products)

    except Exception as e:
        return render_template('error.html', error=str(e), products=products)

'''
Update password screen:
Requires user to input current password, new password, and password confirmation
The current password is checked to see if it matches with the database password
New password is checked with regex to make sure it follows password requirements
then it is check to see if it matches the password confirmation.
If all three checks are true, then it updates the password on the database.
'''
@app.route('/user/profile/update/password', methods=['POST', 'GET'])
def updatePassword():
    try:
        if session.get('user'):
            data = Users.find_one({'_id': session.get('user')})
            if request.method == 'POST':
                _password = request.form['inputPassword']
                _newpswd = request.form['newPassword']
                _confirmpswd = request.form['confirmPassword']
                _regex = '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}'

                # Check if password entered matches user's current password
                if sha256_crypt.verify(_password, data['password']):
                    # check if new password matches passwrod requirements
                    if re.match(_regex, _newpswd):
                    # Check if new password matches password confirmation
                    # if it does, then hash it and update it 
                        if _newpswd == _confirmpswd:
                            _newpswd = sha256_crypt.hash(_newpswd)
                            new_password = {'$set': {'password': _newpswd}}
                            try:
                                Users.update_one({'_id': session.get('user')}, new_password)
                                flash('Password updated.')
                                return redirect(url_for('updateProfile'))
                            except Exception as e:
                                flash(str(e))
                                return redirect(url_for('updateProfile'))
                        else:
                            flash("Passwords do not match.")
                            return redirect(url_for('updateProfile'))
                    else:
                        flash("Password requirements:\n* at least one number\n* at least one uppercase letter\n* at least one lowercase letter\n* must be at least 8 or more characters.")
                        return redirect(url_for('updateProfile'))
                else:
                    flash("Your password is not correct.")
                    return redirect(url_for('updateProfile'))

        else:
            return render_template('error.html', error=str(e), products=products)
    except Exception as e:
        return render_template('error.html', error=str(e), products=products) 

'''
Email update screen:
Checks if email input exists on the database and updates it if it does.
'''
@app.route('/user/profile/update/email', methods=['POST', 'GET'])   
def updateEmail():
    try:
        if session.get('user'):
            if request.method == 'POST':
                _email = request.form['inputEmail']
                if _email != None:
                    new_email = {'$set': {'email': _email}}
                try:
                    Users.update_one({'_id': session.get('user')}, new_email)
                    flash('Email updated.')
                    return redirect(url_for('updateProfile'))
                except Exception as e:
                    flash(str(e))
                    return redirect(url_for('updateProfile'))
        else:
            return render_template('error.html', error="Unauthorized Access", products=products)

    except Exception as e:
        return render_template('error.html', error=str(e), products=products)

'''
Delete Account page
Display page for account deletion. User delets account by pressing submit button.
'''
@app.route('/user/profile/delete', methods=['POST', 'GET'])
def deleteAccount():
    try:
        if session.get('user'):
            data = Users.find_one({'_id': session.get('user')})
            user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
            cart_quantity = 0
            for item in user_cart:
                cart_quantity += Decimal(str(item['quantity']))

            return render_template('/profile/deleteAccount.html', data=data, cart_quantity=cart_quantity, brands=brands, products=products)
        else:
            return render_template('error.html', error='Unauthorized Access',products=products)
    except Exception as e:
        return render_template('error.html', error=str(e), products=products)

'''
Account Deletion confirmation screen:
Display confirmation screen and removes the user from the database and the session
'''
@app.route('/user/profile/delete/confirm', methods=['GET','POST'])
def confirmDelete():
    try:
        if session.get('user'):
            Users.delete_one({'_id': session.get('user')})
            session.pop('user', None)
            return render_template('/profile/displayAccountDelete.html', products=products)
        else:
            return render_template('error.html', error="Unauthorized Access", products=products)
    except Exception as e:
        return render_template('error.html', error=str(e), products=products)

'''***** end profile edits *****'''

'''
Order History:
Shows order history for each account.
Need to find an algorithm to group orders by confirmation number.
'''
@app.route('/account/orderHistory')
def orderHistory():
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        history = [item for item in Order_History.find()]

        order_history = []
        for product in history:
            if product['user_id'] == session.get('user'):
                order_history.append(product)
            
        for product in order_history:
            product['quantity'] = float(product['quantity'])
            product['price'] = float(str(product['price']))
        
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        return render_template('orderHistory.html', data=data, order_history=order_history, cart_quantity=cart_quantity, brands=brands, products=products)
    else:
        return redirect('/showSignIn')

'''
Cart checkout page:
Display a checkout page with address and credit card forms
Also displays a price total 
'''        

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    if session.get('user'):
        data = Users.find_one({'_id': session.get('user')})
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += Decimal(str(item['quantity']))

        if request.method == 'GET':
            subtotal = request.args.get('subtotal')
            tax = request.args.get('tax')
            total = request.args.get('total')
        return render_template('checkout.html', data=data, subtotal=subtotal, tax=tax, total=total, states=states, cart_quantity=cart_quantity, brands=brands, products=products)
    else:
        flash('Please sign in to have access to your cart.')
        return redirect('showSignIn')

'''
Process Payment: 
Gets the user cart information and updates the stock value on the Inventory collection and updates the user order history and deletes the items in the user cart
'''
@app.route('/processPayment', methods=['GET','POST'])
def processPayment():
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        user_cart = [item for item in Cart.find() if item['user_id'] == session.get('user')]
        confirmation = str(uuid.uuid1())
        now = datetime.datetime.now()
        date = now.strftime("%m/%d/%Y, %H:%M:%S")
        temp_cart = user_cart
        if user_cart != None:
            for product in user_cart:
                temp_product = Inventory.find_one(product['_id'])
                if temp_product != None:
                    Inventory.update_one({'_id': temp_product['_id']}, {
                        '$set': {
                            'stock': temp_product['stock'] - int(product['quantity'])
                        }
                    })
                    Cart.delete_one(product)
                    product.update({'_id': str(uuid.uuid1())})
                    product.update({'datetime': date})
                    product.update({'confirmation': confirmation})
                    Order_History.insert_one(product)
        return render_template('orderConfirmation.html', data=user_data, cart=temp_cart, confirmation=confirmation, brands=brands, products=products)
    else:
        flash('Please sign in to have access to your cart')
        return redirect('/showSignIn')

''' ***** Begin cart pages ***** '''

@app.route('/cart', methods=['POST', 'GET'])
def shopping_cart():
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        # Get cart items for the user in session matching user id.
        user_cart = [item for item in Cart.find() if item['user_id'] == user_data['_id']]
        for item in user_cart:
            item['price'] = Decimal(str(item['price']))
            item['quantity'] = Decimal(str(item['quantity']))
        
        # Get cart quantity to display in navbar badge
        cart_quantity = 0
        for item in user_cart:
            cart_quantity += item['quantity']

        return render_template('cart.html', data=user_data, cart=user_cart, cart_quantity=cart_quantity, brands=brands, products=products)
    else:
        flash('Please sign in to have access to your cart.')
        return redirect('/showSignIn')

@app.route('/cart/update/<id>', methods=['POST','GET'])
def updateCart(id):
    if session.get('user'):
        query = {'_id': id, 'user_id': session.get('user')}
        cart_item = Cart.find_one(query)
        item_qty = request.form.get('item-qty')
        product = Inventory.find_one(cart_item['_id'])

        if request.method == 'POST':
            if cart_item != None:
                if int(item_qty) > product['stock']:
                    flash("ERROR: Unable to update cart. Your quantity is higher than the available stock amount.")
                    return redirect('/cart')
                else:
                    Cart.update_one(cart_item, {
                        '$set': {
                            'quantity': item_qty
                        }
                    })
                    flash("Your cart has been updated.")
        return redirect('/cart')
    else:
        flash('Please log in to access your cart.')
        return redirect("/showSignIn")

@app.route('/cart/delete/<id>', methods=['POST', 'GET'])
def deleteCartItem(id):
    if session.get('user'):
        query = {'_id': id, 'user_id': session.get('user')}
        product = Cart.find_one(query)
        if product != None:
            Cart.delete_one(product)
            flash("Item removed successfully.")
        else:
            flash("There was a problem removing your item.")
        return redirect('/cart')
    else:
        flash("Please log in to access your cart.")
        return redirect("showSignIn")

@app.route('/cart/add/<id>', methods=['POST', 'GET'])
def addToCart(id):
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        item_to_add = {'_id': id}
        # Find the product on the Inventory database
        product = Inventory.find_one(item_to_add)
        
        # Get the desired cart quantity
        if request.method == 'POST':
            item_qty = request.form.get('item-qty')
            if int(item_qty) > product['stock']:
                flash("ERROR: Unable to update cart. Your quantity is higher than the available stock amount.")
                return redirect(request.referrer)

        # If the product is found on the Inventory, then add it to the user's cart.
        if product != None:
            product.update({'user_id': user_data['_id']})
            product.update({'quantity': item_qty})

            # if the element already exists, update the quantity - if an item exists for the current user
            # Else insert it
            if Cart.find_one({'_id': product['_id']}):
                Cart.update({'_id': id, 'user_id': user_data['_id']}, {
                    '$set': {
                        'quantity': request.form.get('item-qty')
                    }
                })
                flash("Your cart has been updated.")
            else:
                Cart.insert_one(product)
                flash("Your cart has been updated.")
        # return redirect('/cart')
        return redirect(request.referrer)
    else:
        flash("Please log in to access your cart.")
        return redirect("/showSignIn")

''' ***** End Cart pages *****'''


# ***** Login and sigup routing *****

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        data = Users.find_one({"email": _email.lower()})
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
    return render_template('signin.html', brands=brands, products=products)


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html', brands=brands, products=products)


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

# ***** End log-in and sign-up logic and routing *****

# CRUD for admin page
# List all inventory
@app.route('/admin', methods=['GET', 'POST'])
def showAdminDashboard():
   
    if session.get('user'):
        user_data = Users.find_one({'_id': session.get('user')})
        inventory_data = [item for item in Inventory.find()]

        if user_data:
            if user_data['isAdmin'] == '1':
                return render_template('/admin/admin.html', data=user_data, inventory=inventory_data, brands=brands, products=products)
            else:
                return render_template('error.html', error='Unauthorized Access', data=user_data)
    else:
        return render_template('error.html', error="Unauthorized Access")


# delete - soft delete item
@app.route('/admin/delete/<id>', methods=['GET', 'POST'])
def deleteItem(id):

    if session.get('user'):
        query = {'_id': id}
        user_id = session.get('user')
        now = datetime.datetime.now()
        date = now.strftime("%m/%d/%Y, %H:%M:%S")
        isDeleted = { '$set': {'isDeleted': True, 'deleted_by': user_id, 'deleted_date': date}}
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

        return render_template('/admin/updateItem.html', data=user_data, inventory_item=inventory_item, updated = updated, brands=brands, products=products)
    else:
        return render_template('error.html', error="Unauthorized Access")



# Create - new inventory
@app.route('/admin/create', methods=['GET', 'POST'])
def createItem():
    # brands = [{'name': 'hunter'}, {'name': 'rainbird'}, {'name': 'weathermatic'}]
    # category = [{'name': 'controller'}, {'name': 'rotors'}, {'name': 'sprinkler-body'}, {'name': 'sprinkler-nozzles'}, {'name': 'valves'}]
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
                        'category': _productCategory,
                        'brand': _productBrand,
                        'stock': int(_productStock),
                        'imageUrl': 'static/img/'+_productBrand+'/'+_productCategory+'/'+_productImage
                    }
                    Inventory.insert_one(new_item)
                    inserted = 'true'
                    # Item was inserted successfully.
                elif _productName and _productPrice and _productCategory and _productBrand and _productStock:
                    new_item = {
                        '_id': str(uuid.uuid1()),
                        'productName': _productName,
                        'price': float(_productPrice),
                        'category': _productCategory,
                        'brand': _productBrand,
                        'stock': int(_productStock)
                    }
                    Inventory.insert_one(new_item)
                    inserted = 'true'
                else:
                    #  All fields must be filled out.
                    inserted = 'false'

            except Exception as e:
                return str(e)

        if user_data:
            if user_data['isAdmin'] == '1':
                return render_template('/admin/createItem.html', data=user_data, brands=brands, products=products, response=inserted) 
            else:
                return render_template('error.html', error='Unauthorized Access', data=user_data)
    else:
        return render_template('error.html', error="Unauthorized Access")

# ***** End admin pages *****


if __name__ == '__main__':
    app.run()