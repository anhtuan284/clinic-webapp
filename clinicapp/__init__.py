from flask import Flask
from urllib.parse import quote

from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_cors import CORS

import cloudinary

app = Flask(__name__)

app.secret_key = '^%^&%^(*^^&&*^$%((^^&$$&^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/clinicdb?charset=utf8mb4" % quote('123456')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

cloudinary.config(cloud_name='dwvkjyixu', api_key='536683637118642', api_secret='FskS9miJ-HPA2-27m4vqpokOov4')
db = SQLAlchemy(app)
login = LoginManager(app)
Babel(app)
cors = CORS(app)


# VNPAY CONFIG
VNPAY_RETURN_URL = 'http://127.0.0.1:5000/payment_return_vnpay'  # get from config
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # get from config
VNPAY_API_URL = 'https://sandbox.vnpayment.vn/merchant_webapi/api/transaction'
VNPAY_TMN_CODE = 'F9GSCV1D'  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = 'JUXOOOXYAUTGHZIWOZVOLQCICSTVEACX'  # Secret key for create checksum,get from config

# MOMO
endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
access_key = "F8BBA842ECF85"
secret_key = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
redirect_url = "http://127.0.0.1:5000/payment_return_momo"
ipn_url = "http://127.0.0.1:5000/"

TIENKHAM = 1
SOLUONGKHAM = 2

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'peteralwaysloveu@gmail.com'
EMAIL_HOST_PASSWORD = "uvbc jfpm udxt apwv"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'peteralwaysloveu@gmail.com'
app.config['MAIL_PASSWORD'] = "uvbc jfpm udxt apwv"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 587
