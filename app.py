from flask import Flask, render_template, request, json, redirect, flash
from flaskext.mysql import MySQL
from flask import session, url_for
import re

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'web_store'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql.init_app(app)

app.secret_key = 'cs6314.0w1'
@app.route('/')
def main():
    return render_template("index.html")

@app.route('/userLanding')
def showUserLanding():
    if session.get('user'):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tbl_user WHERE userid = %s', session.get('user'))
        data = cursor.fetchall()
        return render_template('userLanding.html', data=data)
    else:
        return render_template('error.html', error="Unauthorized Access")

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tbl_user WHERE email = %s', (_email))
        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][4] == _password):
                session['user'] = data[0][0]
                return "True"
            else:
                return "Wrong email address or password."
        else:
            return "Wrong email address or password."
    except Exception as e:
        return render_template('error.html', error=str(e))

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
        conn = mysql.connect()
        cursor = conn.cursor()

        # Check if the email address is already in the database.
        # returns 1 if the email is already registered
        if len(_email) != 0:
            cursor.execute('SELECT * FROM tbl_user WHERE email = %s', (_email))
            data = cursor.fetchall()
            if len(data) > 0:
                return "1"

        # Check if password matches password requirements
        # otherwise, display to the user password requirements.
        if re.match(_regex, _password):
            # Check if password matches password confirmation
            # If it does, insert it to the database and create a new user.
            # Otherwise display password does not match error.
            if _password == _confirmpswd:
                cursor.execute("INSERT INTO tbl_user(fname, lname, email, password) VALUES (%s, %s, %s, %s)", (_fname, _lname, _email, _password))
                data = cursor.fetchall()
                # If nothing is returned by the database then commit
                if len(data) == 0:
                    conn.commit()
                    return "User created succesfully. Please log in."
                else:
                    return json.dumps({'error': str(data[0])})
            else:
                return "Passwords do not match."
        else:
            return "Password requirements:\n* at least one number\n* at least one uppercase letter\n* at least one lowercase letter\n* must be at least 8 or more characters."
    else:
        return "Please enter the required fields."

if __name__ == '__main__':
    app.run()