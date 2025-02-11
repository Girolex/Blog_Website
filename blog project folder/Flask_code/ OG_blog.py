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

#Runt the app if this file is executed
if __name__ == '__main__':
    app.run(debug = True)
