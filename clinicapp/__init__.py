from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel

import cloudinary
app = Flask(__name__)

app.secret_key = '^%^&%^(*^^^&&*^(*^^&$$&^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/clinicdb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

cloudinary.config(cloud_name='dwvkjyixu', api_key='536683637118642', api_secret='FskS9miJ-HPA2-27m4vqpokOov4')
db = SQLAlchemy(app)
login = LoginManager(app)
Babel(app)

# VNPAY CONFIG
VNPAY_RETURN_URL = 'http://127.0.0.1:5000/payment-return'  # get from config
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # get from config
VNPAY_API_URL = 'https://sandbox.vnpayment.vn/merchant_webapi/api/transaction'
VNPAY_TMN_CODE = 'F9GSCV1D'  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = 'JUXOOOXYAUTGHZIWOZVOLQCICSTVEACX'  # Secret key for create checksum,get from config
