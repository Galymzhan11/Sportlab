import requests
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, login_required, LoginManager, logout_user, UserMixin

app = Flask(__name__)
app.secret_key = "Galym2021"
db = SQLAlchemy()
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Final.db"
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    surName = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    name = db.Column(db.String)
    color = db.Column(db.String)
    price  = db.Column(db.Float)
    amount = db.Column(db.Integer)
    image = db.Column(db.String)

with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        fname = current_user.name
    else:
        fname = ''
    return render_template('Home.html', is_authenticated=current_user.is_authenticated, fname=fname)

@app.route('/Profile', methods = ["GET", "POST"])
@login_required
def prof():
    if request.method == "POST":
        if current_user.is_authenticated:
            a = True
            fname = current_user.name
            sname = current_user.surName
            email = current_user.email
            password = current_user.password
            newfname = request.form.get('NFirst name')
            newsname = request.form.get('NSecond name')
            newemail = request.form.get('NUser Email')
            newpassword = request.form.get('NPassword')
            data = User.query.filter_by(email=email).first()
            data2 = User.query.filter_by(email=newemail).first()
            if (not newemail.endswith('.com')) and (not newemail.endswith('.ru')):
                a = False

            if data2:
                flash('This email is already exist.', category='error')
            elif len(newemail) < 4 or a is False:
                flash('Email entered incorrectly!', category='error')
            elif len(newsname) < 2 or len(newfname) < 2:
                flash('Your name must be at least 2 character!', category='error')
            elif len(newpassword) < 7:
                flash('Password must be at least 7 character!', category='error')
            else:
                if not data2:
                    if fname != newfname:
                        data.name = newfname
                    if sname != newsname:
                        data.surName = newsname
                    if email != newemail:
                        data.email = newemail
                    if password != newpassword:
                        data.password = newpassword

                    db.session.commit()
                else:
                    flash("This email is already taken!", category='error')
            return redirect(url_for('prof'))

    else:
        return render_template('Profile.html',
                            is_authenticated=current_user.is_authenticated,
                            fname=current_user.name,
                            sname = current_user.surName,
                            email= current_user.email)

@app.route('/Catalog', methods = ["GET", "POST"])
def catalog():
    category = 'Shoes'
    if current_user.is_authenticated:
        fname = current_user.name
    else:
        fname = ''
    prod = Products.query.filter_by(category=category).first()
    print(prod)
    return render_template('Catalog.html',
        is_authenticated=current_user.is_authenticated,
        fname=fname, category = prod.category,
        name = prod.name, color = prod.color, price = prod.price, amount = prod.amount, image = prod.image)


@app.route('/Logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/Login', methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('UserEmail')
        password = request.form.get('Password')
        data = User.query.filter_by(email = email).first()
        if(data and password == data.password):
            login_user(data)
            return redirect(url_for('prof'))
        else:
            flash('Incorrect password or email, try again', category='error')
    return render_template('Login.html')

@app.route('/Register', methods = ["GET", "POST"])
def reg():
    b = True
    if(request.method == 'POST'):
        fname = request.form.get('First name')
        sname = request.form.get('Second name')
        email = request.form.get('User Email')
        password = request.form.get('Password')
        if (not email.endswith('.com')) and (not email.endswith('.ru')):
            b = False

        data = User.query.filter_by(email = email).first()
        if data:
            flash('This email is already exist.', category='error')
        elif len(email) < 4 or b is False:
            flash('Email entered incorrectly!', category='error')
        elif len(sname) < 2 or len(fname) < 2:
            flash('Your name must be at least 2 character!', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 character!', category='error')

        else:
            flash('Account created!', category='success')
            user = User(name=fname,
                        surName=sname,
                        email=email,
                        password=password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('Register.html')

if __name__ == '__main__':
    app.run(debug=True)