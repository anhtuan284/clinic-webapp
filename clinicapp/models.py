import datetime
import hashlib

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


class UserRole(Enum):
    ADMIN = 'admin'
    BENHNHAN = 'patient'
    BACSI = 'doctor'
    YTA = 'nurse'


class User(db.Model, UserMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ten = Column(String(100))
    sdt = Column(String(14), default="0299234422")
    avatar = Column(String(100), default="https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg")
    email = Column(String(100), unique=True)
    dia_chi = Column(String(100), default="Địa chỉ")
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    gioi_tinh = Column(EnumType(Gender), default=Gender.MALE)
    role = Column(EnumType(UserRole), nullable=False)

    def __str__(self):
        return self.name


class Admin(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    quyDinhs = relationship('QuyDinh', backref='admin', lazy=True)


class Doctor(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    phieuKhams = relationship("PhieuKham", backref="doctor", lazy=True)


class Nurse(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    dsNgayKhams = relationship('DanhSachNgayKham', backref="nurse", lazy=True)


class Patient(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    phieuKhams = relationship("PhieuKham", backref="patient", lazy=True)

    lichKhams = relationship('LichKham', backref='patient', lazy=True)


class BaseModel(db.Model):
    __abstract__ = True
    created_date = Column(DateTime, default=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())


class QuyDinh(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ten = Column(String(100))
    gia_tri = Column(String(100), nullable=False)

    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)


class DanhSachNgayKham(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date, unique=True)
    cac_lich_kham = relationship('LichKham', backref='danh_sach_kham', lazy=True)

    yta_id = Column(Integer, ForeignKey(Nurse.id), nullable=False)

    def __str__(self):
        return f"Danh sách khám ngày {self.ngay_kham}"


class LichKham(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date)
    gio_kham = Column(Time)
    xac_nhan = Column(Boolean, default=False)
    thanh_toan = Column(Boolean, default=False)
    trang_thai = Column(Boolean, default=False)

    danhSachKham_id = Column(Integer, ForeignKey(DanhSachNgayKham.id), nullable=False)
    benhnhan_id = Column(Integer, ForeignKey(Patient.id), nullable=False)


    def __str__(self):
        return f"Lịch khám ngày {self.ngay_kham}, giờ {self.gio_kham}, trạng thái {self.trang_thai}"


# class PhieuKham(BaseModel):
#     __tablename__ = 'PhieuKham'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     ngay_kham = Column(Date, default=lambda: datetime.now().date())
#     gio_kham = Column(Time, default=lambda: datetime.now().time())
#     trieu_chung = Column(String(1000))
#     chuan_doan = Column(String(1000))
#     bacsi_id = Column(Integer, ForeignKey('Doctor.id'), nullable=False)
#     benhnhan_id = Column(Integer, ForeignKey('Patient.id'), nullable=False)
#     lichkham = relationship("LichKham", back_populates="phieukham")
#
#
#     bacsi = relationship('Doctor', backref='phieukham_bacsi')
#     benhnhan = relationship('Patient', backref='phieukham_benhnhan')
#     thuoc_phieukham = relationship("Thuoc", secondary="ThuocChiDinh")
#
#     def __str__(self):
#         return f"Phieu khám ngày {self.ngay_kham}, giờ {self.gio_kham}, triệu chứng {self.trieu_chung}, chuẩn đoán {self.chuan_doan}"


class PhieuKham(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ngay_kham = Column(Date, default=lambda: datetime.now().date())
    gio_kham = Column(Time, default=lambda: datetime.now().time())
    trieu_chung = Column(String(1000))
    chuan_doan = Column(String(1000))
    bacsi_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)
    benhnhan_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
    lichKham_id = Column(Integer, ForeignKey(LichKham.id), nullable=False)

    def __str__(self):
        return f"Phieu khám ngày {self.ngay_km}, giờ {self.gio_kham}, triệu chứng {self.trieu_chung}, chuẩn đoán {self.chuan_doan}"


class Thuoc(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    gia = Column(DECIMAL(10, 2))
    name = Column(String(100))
    cach_dung = Column(String(50))
    han_su_dung = Column(Date)

    thuochidinh = relationship("ThuocChiDinh", backref='thuoc', lazy=True)

    def __str__(self):
        return f"Thuoc tên {self.name}, cách dùng {self.cach_dung}, giá {self.gia}"


class DonVi(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    ten = Column(String(100), nullable=False)

    thuoc = relationship("ThuocChiDinh", backref="donvi", lazy=True)


class ThuocChiDinh(db.Model):
    so_luong = Column(Integer)
    cach_dung = Column(String(100))

    phieukham_id = Column(Integer, ForeignKey(PhieuKham.id), primary_key=True)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.id), primary_key=True)
    donVi_id = Column(Integer, ForeignKey(DonVi.id), nullable=False)


class HoaDon(BaseModel):
    ngay_kham = Column(Date, unique=True)
    tien_kham = Column(DECIMAL(10, 2))
    tien_thuoc = Column(DECIMAL(10, 2))
    tong_tien = Column(DECIMAL(11, 2))

    phieuKham_id = Column(Integer, ForeignKey(PhieuKham.id), primary_key=True)

    def __str__(self):
        return f"Hóa đơn phiếu khám {self.phieuKham_id.id}"


class DanhMuc(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))


class DanhMucThuoc(BaseModel):
    danhmuc_id = Column(Integer, ForeignKey(DanhMuc.id), nullable=False, primary_key=True)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.id), primary_key=True, nullable=False)

    def __str__(self):
        return f"Danh mục {self.danhmuc_id} - Thuốc {self.thuoc_id}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        new_user = User(
            ten='Admin',
            sdt='0123456789',
            avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
            email='admin@example.com',
            dia_chi='Admin Site',
            username='admin',
            password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
            gioi_tinh=Gender.MALE,
            role=UserRole.ADMIN,
        )
        db.session.add_all([new_user])
        db.session.commit()
        new_doctor = Doctor(id=new_user.id)
        db.session.add_all([new_doctor])
        db.session.commit()
