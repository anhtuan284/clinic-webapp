import datetime

import bcrypt
import cloudinary.uploader
from io import BytesIO

import pytz


def hash_password(password, rounds=12):
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def crop_to_square(image):
    min_size = min(image.size)

    left = (image.width - min_size) / 2
    top = (image.height - min_size) / 2
    right = (image.width + min_size) / 2
    bottom = (image.height + min_size) / 2

    return image.crop((left, top, right, bottom))


def upload_image_to_cloudinary(image):
    try:
        img_buffer = BytesIO()
        RGB_img = image.convert('RGB')
        RGB_img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)

        upload_result = cloudinary.uploader.upload(img_buffer, folder="avatars")
        if upload_result:
            return upload_result['secure_url']
        else:
            return None
    except Exception as e:
        print("Error uploading image to Cloudinary:", e)
        return None


def datetime_now_vn():
    utc_time = datetime.datetime.utcnow()
    # Tạo đối tượng múi giờ UTC
    utc_timezone = pytz.timezone('UTC')
    # Chuyển đổi thời gian từ UTC sang múi giờ Việt Nam
    vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    vn_time = utc_time.replace(tzinfo=utc_timezone).astimezone(vn_timezone)
    return vn_time
