from flask import Flask, flash, redirect , url_for , render_template , request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, TextAreaField, BooleanField
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import markdown
import os
import secrets
import uuid
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, URL, Length




# create a flask app instace 
app = Flask(__name__)

#add the data base
# --- Database: Railway Postgres in production, SQLite locally ---
db_url = os.environ.get("DATABASE_URL")

if db_url:
    
    db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Upload folder 
app.config["UPLOAD_FOLDER"] = os.environ.get(
    "UPLOAD_FOLDER",
    os.path.join(app.root_path, "static", "uploads")
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


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
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)
    projects = db.relationship("Project", backref="author", lazy=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    body_markdown = db.Column(db.Text, nullable=False)

    thumbnail = db.Column(db.String(200), nullable=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class PostForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired(), validators.Length(min=2, max=150)])
    body_markdown = TextAreaField("Body (Markdown)", [validators.DataRequired()])
    is_featured = BooleanField("Featured")

    thumbnail = FileField("Thumbnail", validators=[FileAllowed(["jpg", "jpeg", "png", "webp", "gif"], "Images only!")])


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    github_url = db.Column(db.String(300), nullable=False)

    body_markdown = db.Column(db.Text, nullable=False, default="")

    thumbnail = db.Column(db.String(200), nullable=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class ProjectForm(FlaskForm):
    title = StringField("Title", [validators.DataRequired()])
    short_description = TextAreaField("Short Description", [validators.DataRequired()])
    github_url = StringField("GitHub URL", [validators.DataRequired()])
    is_featured = BooleanField("Featured?")

    thumbnail = FileField("Thumbnail", validators=[
        FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")])  

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


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)

def save_image(file_storage):
    ext = os.path.splitext(file_storage.filename)[1].lower()  # ".png"
    filename = secure_filename(os.path.splitext(file_storage.filename)[0])
    unique_name = f"{filename}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(file_path)
    return unique_name


# Define a route and a view function
@app.route("/")
def home():
     featured_posts = Post.query.filter_by(is_featured=True).order_by(Post.created_at.desc()).all()
     featured_projects = Project.query.filter_by(is_featured=True).order_by(Project.created_at.desc()).all()

     all_posts = Post.query.order_by(Post.created_at.desc()).all()
     
     return render_template("index.html", featured_posts=featured_posts, featured_projects=featured_projects)

@app.route("/blog")
def blog_list():
    page = request.args.get("page", 1, type=int)
    per_page = 12  # posts per page

    pagination = (Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    )

    posts = pagination.items

    return render_template("blog_list.html",posts=posts,pagination=pagination)



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

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    admin_required()

    form = PostForm()

    if form.validate_on_submit():
        thumbnail_filename = None
        file = request.files.get("thumbnail")

        if file and file.filename:
            thumbnail_filename = save_image(file)

        post = Post(
            title=form.title.data,
            body_markdown=form.body_markdown.data,
            is_featured=bool(form.is_featured.data),
            thumbnail=thumbnail_filename,
            author_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()
        flash("Post created!", "success")
        return redirect(url_for("view_post", post_id=post.id))

    return render_template("create_post.html", form=form)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)

    rendered_body = markdown.markdown(post.body_markdown)

    return render_template("post.html", post=post, rendered_body=rendered_body)

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    admin_required()

    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)  # pre-fills title/body_markdown/is_featured

    if form.validate_on_submit():
        post.title = form.title.data
        post.body_markdown = form.body_markdown.data
        post.is_featured = bool(form.is_featured.data)
        
        file = request.files.get("thumbnail")
        if file and file.filename:
            post.thumbnail = save_image(file)

        db.session.commit()
        flash("Post updated!", "success")
        return redirect(url_for("view_post", post_id=post.id))

    return render_template("edit_post.html", form=form, post=post)

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    admin_required()

    post = Post.query.get_or_404(post_id)

    # --- delete thumbnail file from disk (if it exists) ---
    if post.thumbnail:
        thumbnail_path = os.path.join(
            app.config["UPLOAD_FOLDER"],post.thumbnail 
        )
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted.", "info")
    return redirect(url_for("blog_list"))


@app.route("/projects")
def projects():
    page = request.args.get("page", 1, type=int)
    per_page = 12

    pagination = (Project.query.order_by(Project.id.desc())
               .paginate(page=page, per_page=per_page, error_out=False))

    projects = pagination.items

    return render_template("projects.html",projects=projects,pagination=pagination)

@app.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    if not current_user.is_admin:
        abort(403)

    form = ProjectForm()

    if form.validate_on_submit():
        thumbnail_filename = None
        file = form.thumbnail.data

        if file and hasattr(file, "filename") and file.filename:
            thumbnail_filename = save_image(file)

        project = Project(
            title=form.title.data,
            short_description=form.short_description.data,
            github_url=form.github_url.data,
            body_markdown="",
            is_featured=form.is_featured.data,
            thumbnail=thumbnail_filename,
            author_id=current_user.id
        )

        db.session.add(project)
        db.session.commit()
        flash("Project created!", "success")
        return redirect(url_for("projects"))

    return render_template("project_form.html", form=form, heading="New Project")

@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if not current_user.is_admin:
        abort(403)

    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project.title = form.title.data
        project.short_description = form.short_description.data
        project.github_url = form.github_url.data
        project.is_featured = form.is_featured.data

        file = request.files.get("thumbnail")
        if file and file.filename:
            project.thumbnail = save_image(file)

        db.session.commit()
        flash("Project updated!", "success")
        return redirect(url_for("projects"))

    return render_template("project_form.html", form=form, heading="Edit Project")


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    if not current_user.is_admin:
        abort(403)

    project = Project.query.get_or_404(project_id)

    # --- Delete thumbnail file from disk ---
    if project.thumbnail:
        thumbnail_path = os.path.join(
            app.config["UPLOAD_FOLDER"],project.thumbnail
        )

        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted.", "success")
    return redirect(url_for("projects"))




#displays about info
@app.route("/about")
def about():
    return render_template("about.html")



#Run the app if this file is executed
if __name__ == '__main__':
    app.run()
