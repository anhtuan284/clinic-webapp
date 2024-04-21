import hashlib

from clinicapp import db
from clinicapp.models import User, UserRole


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(ten=name, username=username, password=password, avatar=avatar, role=UserRole.BENHNHAN)
    db.session.add(u)
    db.session.commit()

