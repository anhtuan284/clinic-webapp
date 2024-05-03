import datetime
import hashlib

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Date, Time, DateTime, DECIMAL
from clinicapp import app, db, utils
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
    year_exp = Column(Integer, default=13)
    prescriptions = relationship("Prescription", backref="doctor", lazy=True)


class Nurse(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    appointment_lists = relationship('AppointmentList', backref="nurse", lazy=True)


class Patient(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    height = Column(Integer, default=156)
    weight = Column(Integer, default=55)

    prescriptions = relationship("Prescription", backref="patient", lazy=True)
    appointments = relationship('Appointment', backref='patient', lazy=True)


class Cashier(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)


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
    symptoms = Column(String(1000))
    diagnosis = Column(String(1000))
    doctor_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(Appointment.id))

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
    cashier_id = Column(Integer, ForeignKey(Cashier.id))

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
        # new_user1 = User(
        #     name='Admin',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='admin@example.com',
        #     address='Admin Site',
        #     username='admin',
        #     password=str(utils.hash_password("123")),
        #     cid='092884828822',
        #     gender=Gender.MALE,
        #     role=UserRole.ADMIN,
        # )
        # new_user2 = User(
        #     name='Doctor Strange',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='docter@example.com',
        #     address='Clinic',
        #     username='doctor',
        #     password=str(utils.hash_password("123")),
        #     cid='092884828872',
        #     gender=Gender.MALE,
        #     role=UserRole.DOCTOR,
        # )
        # new_user3 = User(
        #     name='Quốc Huy',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='patient@example.com',
        #     address='Clinic',
        #     username='patient',
        #     password=str(utils.hash_password("123")),
        #     cid='092814828872',
        #     gender=Gender.MALE,
        #     role=UserRole.PATIENT,
        # )
        # db.session.add_all([ new_user3])
        # db.session.commit()
        # # new_doctor = Doctor(id=new_user2.id)
        # # new_admin = Admin(id=new_user1.id)
        # new_patient = Patient(id=new_user3.id)
        # db.session.add_all([ new_patient])
        # db.session.commit()

        # danh_muc_1 = Category(name="Giảm đau")
        # danh_muc_2 = Category(name="Thực phẩm bổ sung")
        # danh_muc_3 = Category(name="Thần Kinh")
        #
        # db.session.add_all([danh_muc_1, danh_muc_2, danh_muc_3])
        # db.session.commit()
        #
        # don_vi_vien = Unit(name="Viên")
        # don_vi_hop = Unit(name="Hộp")
        # don_vi_chai = Unit(name="Chai")
        #
        # db.session.add_all([don_vi_vien, don_vi_hop, don_vi_chai])
        # db.session.commit()
        #
        # # Tạo các loại thuốc (medicine)
        # thuoc_1 = Medicine(name="Panadol", price=10000, usage="Uống sau bữa ăn", exp=datetime.date(2025, 12, 31))
        # thuoc_2 = Medicine(name="Zinc", price=20000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))
        # thuoc_3 = Medicine(name="Vitamin C", price=30000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))
        #
        # db.session.add_all([thuoc_1, thuoc_2, thuoc_3])
        # db.session.commit()
        #
        # cat_med1 = MedicineCategory(category_id=danh_muc_1.id, medicine_id=thuoc_1.id)
        # cat_med2 = MedicineCategory(category_id=danh_muc_2.id, medicine_id=thuoc_1.id)
        # cat_med3 = MedicineCategory(category_id=danh_muc_2.id, medicine_id=thuoc_2.id)
        # cat_med4 = MedicineCategory(category_id=danh_muc_3.id, medicine_id=thuoc_3.id)
        #
        # db.session.add_all([cat_med1, cat_med2, cat_med3, cat_med4])
        # db.session.commit()




# APPOINTMENT CỦA HUY
#         new_user5 = User(
#             name='Quốc Tuấn',
#             phone='0123456789',
#             avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#             email='patient2@example.com',
#             address='Clinic',
#             username='patient2',
#             password=str(utils.hash_password("123")),
#             cid='2654894321',
#             gender=Gender.MALE,
#             role=UserRole.PATIENT,
#         )
#         new_user6 = User(
#             name='Anh Tuấn',
#             phone='0123456789',
#             avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#             email='patient3@example.com',
#             address='Clinic',
#             username='patient3',
#             password=str(utils.hash_password("123")),
#             cid='32589441528',
#             gender=Gender.MALE,
#             role=UserRole.PATIENT,
#         )


        # db.session.add_all([new_user5, new_user6])
        # db.session.commit()
        # new_user4 = User(
        #     name='Thao Van',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='cashier@example.com',
        #     address='Clinic',
        #     username='cashier',
        #     password=str(utils.hash_password("123")),
        #     cid='6854651894',
        #     gender=Gender.FEMALE,
        #     role=UserRole.CASHIER,
        # )
        # db.session.add(new_user4)
        # db.session.commit()
        # new_cashier = Cashier(id=new_user4.id)
        # db.session.add(new_cashier)
        # db.session.commit()

        # new_appointment_list = AppointmentList(
        #     scheduled_date=datetime.date(2024, 4, 25),  # Ngày đặt cuộc hẹn
        #     nurse_id=8  # ID của y tá (Nurse)
        # )
        #
        # # Thêm đối tượng mới vào session và lưu xuống cơ sở dữ liệu
        # db.session.add(new_appointment_list)
        # db.session.commit()

        # new_appointment = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id= 3,  # ID của danh sách đặt hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )
        # new_appointment2 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )
        # new_appointment3 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )
        # new_appointment4 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )
        # new_appointment5 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )

        # new_appointment = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(15, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment2 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(16, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment3 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(8, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment4 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment5 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(11, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=3,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )

        # new_appointment_list = AppointmentList(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     nurse_id=8  # ID của y tá (Nurse)
        # )
        #
        # # Thêm đối tượng mới vào session và lưu xuống cơ sở dữ liệu
        # db.session.add(new_appointment_list)
        # db.session.commit()

        # new_appointment = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(15, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=4,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment2 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(16, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=4,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment3 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(8, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=4,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment4 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=4,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        # new_appointment5 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(11, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     appointment_list_id=4,  # ID của danh sách đặt hẹn
        #     patient_id=11  # ID của bệnh nhân
        # )
        #
        # db.session.add_all([
        #     new_appointment,
        #     new_appointment2,
        #     new_appointment3,
        #     new_appointment4,
        #     new_appointment5
        # ])
        # db.session.commit()

        new_prescription6 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=6

        )
        new_prescription7 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=7

        )
        new_prescription8 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=8

        )
        new_prescription9 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=9

        )
        new_prescription10 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=10

        )
        new_prescription11 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=11

        )
        new_prescription12 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=12

        )
        new_prescription13 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=13

        )
        new_prescription14 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=14

        )
        new_prescription15 = Prescription(
            date=datetime.date(2024, 4, 30),
            symptoms="Ho sổ mũi nhiều đờm",
            diagnosis='Cảm cúm',
            doctor_id=2,
            patient_id=11,
            appointment_id=15

        )
        db.session.add_all([
            new_prescription6,
            new_prescription7,
            new_prescription8,
            new_prescription9,
            new_prescription10,
            new_prescription11,
            new_prescription12,
            new_prescription13,
            new_prescription14,
            new_prescription15,

        ])
        db.session.commit()
