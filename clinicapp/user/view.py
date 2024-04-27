from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Time, DateTime, DECIMAL
from clinicapp import db
from flask_login import UserMixin
from enum import Enum
from sqlalchemy import Enum as EnumType

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'


class Role(Enum):
    ADMIN = 'admin'
    BENHNHAN = 'patient'
    BACSI = 'doctor'
    YTA = 'nurse'


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    phone = Column(String(14))
    avatar = Column(String(100))
    email = Column(String(100), unique=True)
    dia_chi = Column(String(100))
    username = Column(String(50), unique=True)
    password = Column(String(50))
    gender = Column(EnumType(Gender), nullable=False)
    role = Column(EnumType(Role), nullable=False)

    def __str__(self):
        return self.name

