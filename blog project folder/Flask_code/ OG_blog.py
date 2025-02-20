from flask import Flask, redirect , url_for , render_template , request
# create a flask app instace 
app = Flask(__name__)



# Define a route and a view function
@app.route("/")
def home():
    return render_template("index.html")

# this is the login
@app.route("/login", methods = ["POST" , "GET"])
def login():
    return render_template("login.html")

# this leads you to the registration page
@app.route ("/register")
def regiter():
    return render_template("Register.html",  methods = ["POST" , "GET"])

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
