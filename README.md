# flask-python-demo

## Installation

**Create an environment:**

```bash
$ cd yourproject
$ py -3 -m venv venv
```

**Activate the environment:**

```bash
.venv\Scripts\activate
```

**Install Flask Python, Flask SQLAlchemy, Flask Login, Flask WTF**

Within the activated environment, use the following command to install Flask:

```bash
$ pip install flask flask-sqlalchemy
$ pip install flask_login
$ pip install flask_wtf
```
Set up db SQLAlchemy

```bash
$ python
$ from app import app
$ from app import db
$ db.create_all()
```
## Run Flask Python

```bash
$ python app.py
```


