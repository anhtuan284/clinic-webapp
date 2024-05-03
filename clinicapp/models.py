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


class UserRole(Enum):
    ADMIN = 'admin'
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    CASHIER = 'cashier'


class User(db.Model, UserMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    role = Column(EnumType(UserRole), nullable=False)
    name = Column(String(100))
    cid = Column(String(12), unique=True, index=True)
    dob = Column(Date, default=datetime.date.today)
    phone = Column(String(14), default="0299234422")
    email = Column(String(100), unique=True)
    gender = Column(EnumType(Gender))
    address = Column(String(100), default="Địa chỉ")
    avatar = Column(String(100), default="https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg")

    def __str__(self):
        return self.username


class Admin(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    policies = relationship('Policy', backref='admin', lazy=True)


class Doctor(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    prescriptions = relationship("Prescription", backref="doctor", lazy=True)


class Nurse(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    appointment_lists = relationship('AppointmentList', backref="nurse", lazy=True)


class Patient(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    prescriptions = relationship("Prescription", backref="patient", lazy=True)
    appointments = relationship('Appointment', backref='patient', lazy=True)


class BaseModel(db.Model):
    __abstract__ = True
    created_date = Column(DateTime, default=func.now())
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now())


class Policy(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    value = Column(String(100), nullable=False)

    admin_id = Column(Integer, ForeignKey(Admin.id), nullable=False)


class AppointmentList(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    scheduled_date = Column(Date, unique=True)

    appointments = relationship('Appointment', backref='appointment_list', lazy=True)
    nurse_id = Column(Integer, ForeignKey(Nurse.id), nullable=False)

    def __str__(self):
        return f"Appointments List {self.scheduled_date}"


class Appointment(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    scheduled_date = Column(Date)
    scheduled_hour = Column(Time)
    is_confirm = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    status = Column(Boolean, default=False)

    appointment_list_id = Column(Integer, ForeignKey(AppointmentList.id), nullable=True)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)

    def __str__(self):
        return f"Lịch khám ngày {self.scheduled_date}, giờ {self.scheduled_hour}, trạng thái {self.status}"


class Prescription(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    date = Column(Date, default=lambda: datetime.now().date())
    symtoms = Column(String(1000))
    diagnosis = Column(String(1000))
    doctor_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(Appointment.id), nullable=False)

    def __str__(self):
        return f"Phieu khám ngày {self.ngay_km}, giờ {self.gio_kham}, triệu chứng {self.symtoms}, chuẩn đoán {self.diagnosis}"


class Medicine(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    price = Column(DECIMAL(10, 2))
    usage = Column(String(50))
    exp = Column(Date)

    medicine_details = relationship("MedicineDetail", backref='medicine', lazy=True)
    medicine_category = relationship("MedicineCategory", backref='medicine', lazy=True)

    def __str__(self):
        return f"Thuoc {self.name}"


class Unit(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)

    medicine_details = relationship("MedicineDetail", backref="donvi", lazy=True)


class MedicineDetail(db.Model):
    quantity = Column(Integer)
    usage = Column(String(100))

    prescription_id = Column(Integer, ForeignKey(Prescription.id), primary_key=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True)
    unit_id = Column(Integer, ForeignKey(Unit.id), nullable=False)


class Bill(BaseModel):
    service_price = Column(DECIMAL(10, 2))
    medicine_price = Column(DECIMAL(10, 2))
    total = Column(DECIMAL(11, 2))

    prescription_id = Column(Integer, ForeignKey(Prescription.id), primary_key=True)

    def __str__(self):
        return f"Hóa đơn phiếu khám {self.prescription_id.id}"


class Category(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))


class MedicineCategory(BaseModel):
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False, primary_key=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True, nullable=False)

    def __str__(self):
        return f"Danh mục {self.category_id} - Thuốc {self.medicine_id}"


if __name__ == '__main__':
    with app.app_context():
        pass
        # db.create_all()
# # <<<<<<< appoinment
#         new_user = User(
#             name='benh nhan',
#             phone='0905952379',
#             avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#             email='2151013029huy@ou.edu.vn',
#             address='patient Site',
#             username='patient1',
#             password=str(utils.hash_password("123")),
#             gender=Gender.MALE,
#             role=UserRole.PATIENT,
#         )
#         db.session.add_all([new_user])
#         db.session.commit()
#
#         new_doctor = Patient(id=new_user.id)
#         db.session.add_all([new_doctor])
#         db.session.commit()

#         new_appointment_list = AppointmentList(
#             scheduled_date=datetime.date(2024, 4, 25),  # Ngày đặt cuộc hẹn
#             nurse_id=1  # ID của y tá (Nurse)
#         )
# #         #
#
# #         # # Thêm đối tượng mới vào session và lưu xuống cơ sở dữ liệu
#         db.session.add(new_appointment_list)
#         db.session.commit()
#
#         new_appointment = Appointment(
#             scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#             scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
#             is_confirm=False,  # Trạng thái xác nhận
#             is_paid=False,  # Trạng thái thanh toán
#             status=False,  # Trạng thái cuộc hẹn
#             appointment_list_id= None,  # ID của danh sách đặt hẹn
#             patient_id=2  # ID của bệnh nhân
#         )
#
#         db.session.add(new_appointment)
#         db.session.commit()
