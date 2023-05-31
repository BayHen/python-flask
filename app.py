from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, current_user, login_user, UserMixin, logout_user

# Create a Flask Instance
app = Flask(__name__)

# Add Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project_test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATUONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)
app.app_context().push()

# Secret Key
app.config['SECRET_KEY'] = "python-secret-key-flask"

#Config Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(id))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique = True)
    password = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='user')
    date_create = db.Column(db.Date(), default=datetime.utcnow)
    
    def __init__(self, name=None, email=None, password=None, date_create=None):
        self.name = name
        self.email = email
        self.password = password
        self.date_create = date_create
    
class Post(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    blog_name = db.Column(db.String(255), nullable=False, )
    content = db.Column(db.String(100), nullable=False, unique = True)
    date_create = db.Column(db.Date(), default=datetime.utcnow)

    def __init__(self, user_id=None, blog_name=None, content=None, date_create=None):
        self.user_id = user_id
        self.blog_name = blog_name
        self.content = content
        self.date_create = date_create

# Create a From Class

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

# Create Sign In Form
class SignInForm(FlaskForm):
    email = StringField('Enter your email address!!!', validators=[DataRequired()])
    password = PasswordField('Enter your password!!!', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = SignInForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            user = User.query.filter_by(email=form.email.data).first()
            if not user or not check_password_hash(user.password, form.password.data):
                flash('Please check your login details and try again.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
    return render_template('auth/login.html', form=form)
    
# Create Sign Up Form
class SignUpForm(FlaskForm):
    name = StringField('Enter your Name!!!', validators=[DataRequired()])
    email = StringField('Enter your email address!!!', validators=[DataRequired()])
    password = PasswordField('Enter Password!!!', validators=[DataRequired()])
    password_confirm = PasswordField('Enter Password Confirm!!!', validators=[DataRequired()])

@app.route('/user/regist', methods=['GET' ,'POST'])
def sign_up():
    form = SignUpForm()
    if not current_user.is_authenticated:
        if request.method == 'POST':
            if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                session.permanent = True
                if user is None:
                    if form.password.data == form.password_confirm.data:
                            user = User(form.name.data, form.email.data, generate_password_hash(form.password.data))
                            db.session.add(user)
                            db.session.commit()
                            flash("Bạn đã đăng ký thành công!!!!", "info")
                            return redirect(url_for("login"))
                    else:
                        flash("Password đang không trùng khớp!!!!", "info")
                        return redirect(url_for('sign_up'))
                else:
                    flash('Email address already exists')
                    return redirect(url_for('sign_up'))
    else:
        return redirect(url_for('index'))
    return render_template('user/regist.html', form=form)

#Create a new Post Form
class CreatePostForm(FlaskForm):
    blog_name = StringField('Enter your Name!!!', validators=[DataRequired()])
    content = TextAreaField('Enter your email address!!!', validators=[DataRequired()])

@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if current_user.is_authenticated:
        form = CreatePostForm()
        if request.method == 'POST':
            post = Post(current_user.id, form.blog_name.data, form.content.data)
            db.session.add(post)
            db.session.commit()
            flash("Bạn đã đăng ký thành công!!!!", "info")
            return redirect(url_for('index'))
    return render_template('post/create.html', form=form)

#Show Post
@app.route('/user/posts')
@login_required
def show_post():
    if current_user.is_authenticated:
        posts = Post.query.filter_by(user_id=current_user.id)
    return render_template('user/posts.html', posts=posts)

#Create Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#Edit User Profile 
@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = SignUpForm()
    if current_user.is_authenticated:
        user_profile = User.query.filter_by(id=current_user.id)
        if request.method == 'POST':
            if form.validate_on_submit():
                user = User.query.filter_by(email=form.email.data).first()
                session.permanent = True
                if user is None:
                    if form.password.data == form.password_confirm.data:
                            user = User(form.name.data, form.email.data, generate_password_hash(form.password.data))
                            db.session.add(user)
                            db.session.commit()
                            flash("Bạn đã cập nhật thành công!!!!", "info")
                            return redirect(url_for("user"))
                    else:
                        flash("Password đang không trùng khớp!!!!", "info")
                        return redirect(url_for('edit_user'))
                else:
                    flash('Email address already exists')
                    return redirect(url_for('edit_user'))
    else:
        return redirect(url_for('index'))
    return render_template('user/edit.html', form=form, user_profile=user_profile)
            
@app.route('/user/user')
@login_required
def user():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
    return render_template('user/user.html', user=user)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)