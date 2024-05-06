import bcrypt
import cloudinary
from io import BytesIO


def hash_password(password, rounds=12):
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def crop_to_square(image):
    min_size = min(image.size)
    return image.crop((0, 0, min_size, min_size))


def upload_image_to_cloudinary(image):
    try:
        img_buffer = BytesIO()
        image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)

        upload_result = cloudinary.uploader.upload(img_buffer, folder="avatars")
        if upload_result:
            return upload_result['secure_url']
        else:
            return None
    except Exception as e:
        print("Error uploading image to Cloudinary:", e)
        return None