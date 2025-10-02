from flask import Flask, flash, redirect , url_for , render_template , request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

# create a flask app instace 
app = Flask(__name__)
app.secret_key = "random_shite"

class RegistrationForm(FlaskForm):
    name = StringField('name',[validators.DataRequired(), validators.length(min = 2, max = 24)])
    email = StringField('email',[validators.DataRequired(), validators.length(min=6, max = 35)])
    password = PasswordField('password',[validators.DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[validators.EqualTo('password', message = 'password must match')])

# Define a route and a view function
@app.route("/")
def home():
    return render_template("index.html")

# this is the login
@app.route("/login", methods = ["GET" , "POST"])
def login():
    return render_template("login.html")

# this leads you to the registration page
@app.route ("/register", methods = ["GET" , "POST"])
def register():
    form = RegistrationForm()
    if    form.validate_on_submit() : 
        
        flash('registration succesfull')
        print(form.errors)
        return redirect(url_for('login'))
    
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
