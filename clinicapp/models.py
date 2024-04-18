# import datetime
# from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Time, DateTime, DECIMAL
# from clinicapp import app, db
# from sqlalchemy.orm import relationship
# from flask_login import UserMixin
# from enum import Enum
# from sqlalchemy import Enum as EnumType
# from sqlalchemy.sql import func
#
#
# class Gender(Enum):
#     MALE = 'male'
#     FEMALE = 'female'
#
#
# class Role(Enum):
#     ADMIN = 'admin'
#     BENHNHAN = 'patient'
#     BACSI = 'doctor'
#     YTA = 'nurse'
#
#
# class User(db.Model, UserMixin):
#     __tablename__ = 'Users'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     name = Column(String(100))
#     phone = Column(String(14))
#     avatar = Column(String(100))
#     email = Column(String(100), unique=True)
#     dia_chi = Column(String(100))
#     username = Column(String(50), unique=True)
#     password = Column(String(50))
#     gender = Column(EnumType(Gender), nullable=False)
#     role = Column(EnumType(Role), nullable=False)
#
#     def __str__(self):
#         return self.name
#
#
#
#
# class Admin(User):
#     __tablename__ = 'Admin'
#     id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
#
#     __mapper_args__ = {
#         'polymorphic_identity': Role.ADMIN.value
#     }
#
# class Doctor(User):
#     __tablename__ = 'doctors'
#     id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
#     # Thêm các trường riêng cho bác sĩ (nếu cần)
#
#     __mapper_args__ = {
#         'polymorphic_identity': Role.BACSI.value
#     }
#
#
# class Nurse(User):
#     __tablename__ = 'nurses'
#     id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
#     # Thêm các trường riêng cho y tá (nếu cần)
#
#     __mapper_args__ = {
#         'polymorphic_identity': Role.YTA.value
#     }
#
#
# class Patient(User):
#     __tablename__ = 'patients'
#     id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
#     # Thêm các trường riêng cho bệnh nhân (nếu cần)
#
#     __mapper_args__ = {
#         'polymorphic_identity': Role.BENHNHAN.value
#     }
#
# class BaseModel(db.Model):
#     __abstract__ = True
#     created_date = Column(DateTime, default=func.now())
#     updated_date = Column(DateTime, default=func.now(), onupdate=func.now())
#
#
# class QuyDinh(db.Model):
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ten = Column(String(100))
#     gia_tri = Column(String(100), nullable=False)
#
#
# class DanhNgaySachKham(BaseModel):
#     __tablename__ = 'DanhNgaySachKham'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ngay_kham = Column(Date, unique=True)
#     cac_lich_kham = relationship('LichKham', backref='danh_sach_kham', lazy=True)
#
#     def __str__(self):
#         return f"Danh sách khám ngày {self.ngay_kham}"
#
#
# class LichKham(BaseModel):
#     __tablename__ = 'LichKham'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ngay_kham = Column(Date)
#     gio_kham = Column(Time)
#     xac_nhan = Column(Boolean, default=False)
#     thanh_toan = Column(Boolean, default=False)
#     trang_thai = Column(Boolean, default=False)
#
#     DanhSachKham_id = Column(Integer, ForeignKey(DanhNgaySachKham.id), nullable=False)
#
#     def __str__(self):
#         return f"Lịch khám ngày {self.ngay_kham}, giờ {self.gio_kham}, trạng thái {self.trang_thai}"
#
#
# class PhieuKham(BaseModel):
#     __tablename__ = 'PhieuKham'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ngay_kham = Column(Date, default=lambda: datetime.now().date())
#     gio_kham = Column(Time, default=lambda: datetime.now().time())
#     trieu_chung = Column(String(1000))
#     chuan_doan = Column(String(1000))
#     bacsi_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
#     benhnhan_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
#
#     bacsi = relationship('User', backref='phieukham_bacsi', foreign_keys=[bacsi_id])
#     benhnhan = relationship('User', backref='phieukham_benhnhan', foreign_keys=[benhnhan_id])
#     thuoc_phieukham = relationship("Thuoc", secondary="ThuocChiDinh")
#
#     def __str__(self):
#         return f"Phieu khám ngày {self.ngay_kham}, giờ {self.gio_kham}, triệu chứng {self.trieu_chung}, chuẩn đoán {self.chuan_doan}"
#
#
# class Thuoc(BaseModel):
#     __tablename__ = 'Thuoc'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     gia = Column(DECIMAL(10, 2))
#     name = Column(String(100))
#     cach_dung = Column(String(50))
#     han_su_dung = Column(Date)
#
#     def __str__(self):
#         return f"Thuoc tên {self.name}, cách dùng {self.cach_dung}, giá {self.gia}"
#
#
# class DonVi(db.Model):
#     __tablename__ = 'DonVi'
#
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ten = Column(String(100), nullable=False)
#
#     thuoc = relationship("ThuocChiDinh", backref="thuocchidinh_donvi", lazy=False)
#
#
# class ThuocChiDinh(BaseModel):
#     __tablename__ = 'ThuocChiDinh'
#     so_luong = Column(Integer)
#     cach_dung = Column(String(100))
#
#     phieukham_id = Column(Integer, ForeignKey('PhieuKham.id'), primary_key=True)
#     thuoc_id = Column(Integer, ForeignKey('Thuoc.id'), primary_key=True)
#     don_vi = Column(Integer, ForeignKey('DonVi.id'))
#
#     phieukham = relationship("PhieuKham", backref="thuoc_chidinh")
#     thuoc = relationship("Thuoc", backref="phieukham_chidinh")
#
#
# class HoaDon(BaseModel):
#     __tablename__ = 'HoaDon'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ngay_kham = Column(Date, unique=True)
#     tien_kham = Column(DECIMAL(10, 2))
#     tien_thuoc = Column(DECIMAL(10, 2))
#     tong_tien = Column(DECIMAL(11, 2))
#
#     def __str__(self):
#         return f"Hoa đơn {self.ngay_kham}"
#
#
# class DanhMuc(BaseModel):
#     __tablename__ = 'DanhMuc'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     name = Column(String(100))
#
#
# class DanhMucThuoc(BaseModel):
#     __tablename__ = 'DanhMucThuoc'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#
#     danhmuc_id = Column(Integer, ForeignKey('DanhMuc.id'), nullable=False)
#     thuoc_id = Column(Integer, ForeignKey('Thuoc.id'), nullable=False)
#
#     danhmuc = relationship('DanhMuc', backref='danhmuc_thuoc')
#     thuoc = relationship('Thuoc', backref='thuoc_danhmuc')
#
#     def __str__(self):
#         return f"Danh mục {self.danhmuc_id} - Thuốc {self.thuoc_id}"
#
#
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         # c1 = Category(name='Mobile')
#         # c2 = Category(name='Tablet')
#         # c3 = Category(name='Laptop')
#         # db.session.add_all([c1, c2, c3])
#         # db.session.commit()
#         #
#         # import json
#         # with open('data/products.json', encoding='utf-8') as f:
#         #     products = json.load(f)
#         #     for p in products:
#         #         prod = Product(**p)
#         #         db.session.add(prod)
#         #
#         # db.session.commit()
#
#         # import hashlib
#         # u = User(name='admin', username='admin',
#         #          avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1679731974/jlad6jqdc69cjrh9zggq.jpg',
#         #          password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()))
#         # db.session.add(u)
#         # db.session.commit()

import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Time, DateTime, DECIMAL
from clinicapp import app, db
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum
from sqlalchemy import Enum as EnumType
from sqlalchemy.sql import func


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


class Admin(User):
    __tablename__ = 'Admin'
    id = Column(Integer, ForeignKey('Users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': Role.ADMIN.value
    }


class Doctor(User):
    __tablename__ = 'Doctor'
    id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
    # Thêm các trường riêng cho bác sĩ (nếu cần)

    __mapper_args__ = {
        'polymorphic_identity': Role.BACSI.value
    }

    # Mối quan hệ: Một bác sĩ có thể có nhiều phiếu khám
    phieu_kham = relationship("PhieuKham", backref="bacsi")


class Nurse(User):
    __tablename__ = 'Nurse'
    id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
    # Thêm các trường riêng cho y tá (nếu cần)

    __mapper_args__ = {
        'polymorphic_identity': Role.YTA.value
    }


class Patient(User):
    __tablename__ = 'Patient'
    id = Column(Integer, ForeignKey('Users.id'), primary_key=True)
    phieu_kham = relationship("PhieuKham", backref="benhnhan")

    # Thêm các trường riêng cho bệnh nhân (nếu cần)

    __mapper_args__ = {
        'polymorphic_identity': Role.BENHNHAN.value
    }

    # Mối quan hệ: Một bệnh nhân có thể có nhiều phiếu khám
    phieu_khams = relationship("PhieuKham", backref="benhnhan")


class BaseModel(db.Model):
    __abstract__ = True
    created_date = Column(DateTime, default=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())


class QuyDinh(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ten = Column(String(100))
    gia_tri = Column(String(100), nullable=False)


class DanhNgaySachKham(BaseModel):
    __tablename__ = 'DanhNgaySachKham'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date, unique=True)
    cac_lich_kham = relationship('LichKham', backref='danh_sach_kham', lazy=True)
    yta_id = Column(Integer, ForeignKey('Nurse.id'), nullable=False)

    yta = relationship('Nurse', backref='Danhsachngaykham_yta')
    def __str__(self):
        return f"Danh sách khám ngày {self.ngay_kham}"


class LichKham(BaseModel):
    __tablename__ = 'LichKham'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date)
    gio_kham = Column(Time)
    xac_nhan = Column(Boolean, default=False)
    thanh_toan = Column(Boolean, default=False)
    trang_thai = Column(Boolean, default=False)

    DanhSachKham_id = Column(Integer, ForeignKey(DanhNgaySachKham.id), nullable=False)
    benhnhan_id = Column(Integer, ForeignKey('Patient.id'), nullable=False)

    benhnhan = relationship('Patient', backref='phieukham_benhnhan')

    def __str__(self):
        return f"Lịch khám ngày {self.ngay_kham}, giờ {self.gio_kham}, trạng thái {self.trang_thai}"


class PhieuKham(BaseModel):
    __tablename__ = 'PhieuKham'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date, default=lambda: datetime.now().date())
    gio_kham = Column(Time, default=lambda: datetime.now().time())
    trieu_chung = Column(String(1000))
    chuan_doan = Column(String(1000))
    bacsi_id = Column(Integer, ForeignKey('Doctor.id'), nullable=False)
    benhnhan_id = Column(Integer, ForeignKey('Patient.id'), nullable=False)
    lichkham = relationship("LichKham", back_populates="phieukham")


    bacsi = relationship('Doctor', backref='phieukham_bacsi')
    benhnhan = relationship('Patient', backref='phieukham_benhnhan')
    thuoc_phieukham = relationship("Thuoc", secondary="ThuocChiDinh")

    def __str__(self):
        return f"Phieu khám ngày {self.ngay_kham}, giờ {self.gio_kham}, triệu chứng {self.trieu_chung}, chuẩn đoán {self.chuan_doan}"


class Thuoc(BaseModel):
    __tablename__ = 'Thuoc'
    id = Column(Integer, autoincrement=True, primary_key=True)
    gia = Column(DECIMAL(10, 2))
    name = Column(String(100))
    cach_dung = Column(String(50))
    han_su_dung = Column(Date)

    def __str__(self):
        return f"Thuoc tên {self.name}, cách dùng {self.cach_dung}, giá {self.gia}"


class DonVi(db.Model):
    __tablename__ = 'DonVi'

    id = Column(Integer, autoincrement=True, primary_key=True)
    ten = Column(String(100), nullable=False)

    thuoc = relationship("ThuocChiDinh", backref="thuocchidinh_donvi", lazy=False)


class ThuocChiDinh(BaseModel):
    __tablename__ = 'ThuocChiDinh'
    so_luong = Column(Integer)
    cach_dung = Column(String(100))

    phieukham_id = Column(Integer, ForeignKey('PhieuKham.id'), primary_key=True)
    thuoc_id = Column(Integer, ForeignKey('Thuoc.id'), primary_key=True)
    don_vi = Column(Integer, ForeignKey('DonVi.id'))

    phieukham = relationship("PhieuKham", backref="thuoc_chidinh")
    thuoc = relationship("Thuoc", backref="phieukham_chidinh")


class HoaDon(BaseModel):
    __tablename__ = 'HoaDon'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date, unique=True)
    tien_kham = Column(DECIMAL(10, 2))
    tien_thuoc = Column(DECIMAL(10, 2))
    tong_tien = Column(DECIMAL(11, 2))

    def __str__(self):
        return f"Hoa đơn {self.ngay_kham}"


class DanhMuc(BaseModel):
    __tablename__ = 'DanhMuc'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))


class DanhMucThuoc(BaseModel):
    __tablename__ = 'DanhMucThuoc'
    id = Column(Integer, autoincrement=True, primary_key=True)

    danhmuc_id = Column(Integer, ForeignKey('DanhMuc.id'), nullable=False)
    thuoc_id = Column(Integer, ForeignKey('Thuoc.id'), nullable=False)

    danhmuc = relationship('DanhMuc', backref='danhmuc_thuoc')
    thuoc = relationship('Thuoc', backref='thuoc_danhmuc')

    def __str__(self):
        return f"Danh mục {self.danhmuc_id} - Thuốc {self.thuoc_id}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
