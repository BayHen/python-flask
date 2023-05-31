from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
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
app.permanent_session_lifetime = timedelta(minutes=1)
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

    def __init__(self, blog_name=None, content=None, user_id=None, date_create=None):
        self.blog_name = blog_name
        self.content = content
        self.user_id = user_id
        self.date_create = date_create

# Create a From Class

@app.route('/')
def index():
    return render_template('index.html')

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
@login_required
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