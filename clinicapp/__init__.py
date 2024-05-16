import os
import cloudinary
import joblib
from flask import Flask
from dotenv import load_dotenv, dotenv_values
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.secret_key = '^%^&%^(*^^&&*^$%((^^&$$&^'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 4

cloudinary.config(cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
                  api_key=os.environ.get("CLOUDINARY_API_KEY"),
                  api_secret=os.environ.get("CLOUDINARY_API_SECRET"))
db = SQLAlchemy(app)
login = LoginManager(app)
Babel(app)
cors = CORS(app)


# VNPAY CONFIG
VNPAY_RETURN_URL = os.environ.get('VNPAY_RETURN_URL')
VNPAY_PAYMENT_URL = os.environ.get('VNPAY_PAYMENT_URL')
VNPAY_API_URL = os.environ.get('VNPAY_API_URL')
VNPAY_TMN_CODE = os.environ.get('VNPAY_TMN_CODE')
VNPAY_HASH_SECRET_KEY = os.environ.get('VNPAY_HASH_SECRET_KEY')

# MOMO
endpoint = os.environ.get('MOMO_ENDPOINT')
access_key = os.environ.get('MOMO_ACCESS_KEY')
secret_key = os.environ.get('MOMO_SECRET_KEY')
redirect_url = os.environ.get('MOMO_REDIRECT_URL')
ipn_url = os.environ.get('MOMO_IPN_URL')

TIENKHAM = 2
SOLUONGKHAM = 3

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 587
app.config['MAIL_SENDER'] = "PHÒNG KHÁM AN TÂM"
app.config['MAIL_SENDER_EMAIL'] = "phongkhamantam@example.com"

current_directory = os.path.dirname(os.path.abspath(__file__))
model_file_path = os.path.join(current_directory, 'models', 'gradient_boosting_model.joblib')
loaded_model = joblib.load(model_file_path)
