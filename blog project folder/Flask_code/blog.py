from flask import Flask, flash, redirect , url_for , render_template , request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


# create a flask app instace 
app = Flask(__name__)
#add the data base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.secret_key = "random_shite"

#initialize the database
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"         
login_manager.login_message_category = "warning"



#create model
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable =False,unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    name = StringField('name',[validators.DataRequired(), validators.length(min = 2, max = 24)])
    email = StringField('email',[validators.DataRequired(), validators.length(min=6, max = 35)])
    password = PasswordField('password',[validators.DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[validators.EqualTo('password', message = 'password must match')])

class LoginForm(FlaskForm):
    email = StringField('email', [validators.DataRequired(), validators.length(min=6, max=35)])
    password = PasswordField('password', [validators.DataRequired()])

# Define a route and a view function
@app.route("/")
@login_required
def home():
    return render_template("index.html")

# this is the login
@app.route("/login", methods = ["GET" , "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)  


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you have been logged out succesfully!", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return "Secret dashboard "

    
    

# this leads you to the registration page   
@app.route ("/register", methods = ["GET" , "POST"])
def register():
    form = RegistrationForm()
    print("---- REGISTER HIT ----")
    print("method:", request.method)
    print("validate:", form.validate_on_submit())
    if form.is_submitted():
        print("errors", form.errors)
    if    form.validate_on_submit(): 
        
        user = User(name=form.name.data,email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        try:
            db.session.commit()
            print("COMMITTED ", user.id, user.email)
            print("DB:", db.engine.url)
        except IntegrityError:
            db.session.rollback()
            flash("That email is already regitered.", "danger")
            return render_template("Register.html", form=form)
        
      
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    
    if form.is_submitted():
         print("REGISTER SUBMITTED errors:", form.errors)
         print("DB ", db.engine.url)
    return render_template("Register.html", form = form )

#displays whatever you type in the URL
@app.route("/<name>")
def user(name):
    return render_template("User.html", content = name, age = 21)

#displays about info
@app.route("/about_page")
def about():
    return "The about Page"


#redirects you to the home page 
@app.route("/admin")
def admin():
    return redirect(url_for("home"))

#Run the app if this file is executed
if __name__ == '__main__':
    app.run(debug = True)
