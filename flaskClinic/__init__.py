from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$$&^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saledb?charset=utf8mb4" % quote('Baopro123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

cloudinary.config(cloud_name='dwvkjyixu', api_key='536683637118642', api_secret='FskS9miJ-HPA2-27m4vqpokOov4')
db = SQLAlchemy(app)
login = LoginManager(app)