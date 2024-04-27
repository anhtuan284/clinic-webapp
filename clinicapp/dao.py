import hashlib

from clinicapp import db
from clinicapp.models import User, UserRole
from clinicapp.utils import hash_password, verify_password


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    user = User.query.filter_by(username=username.strip()).first()
    if user and verify_password(password.strip(), user.password):
        return user
    return None


def add_user(name, username, password, avatar):
    hashed_password = hash_password(password.strip())
    u = User(ten=name, username=username, password=hashed_password, avatar=avatar, role=UserRole.BENHNHAN)
    db.session.add(u)
    db.session.commit()

