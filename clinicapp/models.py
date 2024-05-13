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
    avatar = Column(String(100),
                    default="https://res.cloudinary.com/dwvkjyixu/image/upload/v1715592288/avatars/pzh51raolcegilwmhm4g.jpg")

    def __str__(self):
        return self.username


class Admin(db.Model):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)

    policies = relationship('Policy', backref='admin', lazy=True)

    def __str__(self):
        return User.query.get(self.id).name


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

    admin_id = Column(Integer, ForeignKey(Admin.id), default=1, nullable=False)


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
    status = Column(Boolean, default=False, nullable=False)

    appointment_list_id = Column(Integer, ForeignKey(AppointmentList.id), nullable=True)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)

    prescription = relationship('Prescription', backref="appointment", lazy=True)

    def __str__(self):
        return f"Lịch khám ngày {self.scheduled_date}, giờ {self.scheduled_hour}, trạng thái {self.status}"


class Prescription(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    date = Column(Date, default=datetime.date.today)
    symptoms = Column(String(1000))
    diagnosis = Column(String(1000))

    doctor_id = Column(Integer, ForeignKey(Doctor.id), nullable=False)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(Appointment.id))

    medicine_details = relationship("MedicineDetail", backref='prescription', lazy=True)

    def __str__(self):
        return f"Phiếu khám ngày {self.date}, triệu chứng {self.symptoms}, chuẩn đoán {self.diagnosis}"


class Medicine(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    price = Column(DECIMAL(10, 2))
    usage = Column(String(50))
    exp = Column(Date)

    medicine_details = relationship("MedicineDetail", backref='medicine', lazy=True)
    medicine_category = relationship("MedicineCategory", backref='medicine', lazy=True)
    medicine_units = relationship("MedicineUnit", backref='medicine', lazy=True)

    def __str__(self):
        return f"Thuốc {self.name}"


class Unit(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)

    medicine_units = relationship("MedicineUnit", backref='unit', lazy=True)

    def __str__(self):
        return self.name


class MedicineUnit(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_id = Column(Integer, ForeignKey(Unit.id))
    medicine_id = Column(Integer, ForeignKey(Medicine.id))
    medicine_details = relationship("MedicineDetail", backref='medicine_unit', lazy=True)
    quantity = Column(Integer)


class MedicineDetail(db.Model):
    quantity = Column(Integer)
    usage = Column(String(100))

    prescription_id = Column(Integer, ForeignKey(Prescription.id), primary_key=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True)
    medicine_unit_id = Column(Integer, ForeignKey(MedicineUnit.id))

    def __str__(self):
        return 'Phiếu khám ngày: ' + str(self.prescription.date) + ', id: ' + str(self.prescription_id)


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
    medicine_category = relationship("MedicineCategory", backref='category', lazy=True)


class MedicineCategory(BaseModel):
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False, primary_key=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True, nullable=False)

    def __str__(self):
        return f"Danh mục {self.category_id} - Thuốc {self.medicine_id}"


class HistoryOnlinePayment(BaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True)
    amount = Column(DECIMAL(11, 2))
    response_code = Column(String(300))
    gateway_name = Column(String(100))
    gateway_name = Column(String(100))
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)
    paid = Column(Boolean, default=False)


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # new_appointment4 = Appointment(
        #     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
        #     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
        #     is_confirm=False,  # Trạng thái xác nhận
        #     is_paid=False,  # Trạng thái thanh toán
        #     status=True,  # Trạng thái cuộc hẹn
        #     patient_id=3  # ID của bệnh nhân
        # )
        # db.session.add(new_appointment4)
        # db.session.commit()
        # order = HistoryOnlinePayment(amount=200000, response_code="aadasdasdasdas", gateway_name="vnpay", patient_id=1)
        # db.session.add(order)
        # db.session.commit()

        new_user4 = User(
            name='Thao Van',
            phone='0123456759',
            avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
            email='cashier11@example.com',
            address='Clinic',
            username='cashier',
            password=str(utils.hash_password("123")),
            cid='68543151894',
            gender=Gender.FEMALE,
            role=UserRole.CASHIER,
        )
        db.session.add(new_user4)
        db.session.commit()

        # db.create_all()
        # new_user1 = User(
        #     name='thungan',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='admin@example.com',
        #     address='Admin Site',
        #     username='admin',
        #     password=str(utils.hash_password("123")),
        #     cid='092884828822',
        #     gender=Gender.MALE,
        #     role=UserRole.CASHIER,
        # )
        #
        # db.session.add(new_user1)
        # db.session.commit()

        # new_user2 = User(
        #     name='Doctor Strange',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='docter@example.com',
        #     address='Clinic',
        #     username='doctorstrange',
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
        # db.session.add_all([ new_user2, new_user3])
        # db.session.commit()
        # new_doctor2 = Doctor(id=8)
        # new_admin = Admin(id=new_user1.id)
        # new_patient = Patient(id=new_user3.id)
        # db.session.add_all([ new_doctor2])
        # db.session.commit()
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
        # db.session.add(new_user1)
        # db.session.commit()
        # new_user2 = User(
        #     name='Doctor Strange',
        #     phone='0123456789',
        #     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
        #     email='docter@example.com',
        #     address='Clinic',
        #     username='doctorstrange',
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
        # db.session.add_all([new_user1, new_user2, new_user3])
        # db.session.commit()
        # new_doctor2 = Doctor(id=new_user2.id)
        # new_admin = Admin(id=new_user1.id)
        # new_patient = Patient(id=new_user3.id)
        # db.session.add_all([new_doctor2, new_admin, new_patient])
        # db.session.commit()
        #
        # danh_muc_1 = Category(name="Giảm đau")
        # danh_muc_2 = Category(name="Thực phẩm bổ sung")
        # danh_muc_3 = Category(name="Thần Kinh")
        #
        # db.session.add_all([danh_muc_1, danh_muc_2, danh_muc_3])
        # db.session.commit()
        #
        # don_vi_vien = Unit(name="Viên")
        # don_vi_hop = Unit(name="Hộp")
        # don_vi_vi = Unit(name="Chai")
        #
        # db.session.add_all([don_vi_vien, don_vi_hop, don_vi_vi])
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
        #
        # med1_unit1 = MedicineUnit(medicine_id=thuoc_1.id, unit_id=don_vi_vien.id, quantity=1)
        # med1_unit2 = MedicineUnit(medicine_id=thuoc_1.id, unit_id=don_vi_hop.id, quantity=23)
        # med1_unit3 = MedicineUnit(medicine_id=thuoc_1.id, unit_id=don_vi_vi.id, quantity=14)
        #
        # med2_unit1 = MedicineUnit(medicine_id=thuoc_2.id, unit_id=don_vi_vien.id, quantity=1)
        # med2_unit2 = MedicineUnit(medicine_id=thuoc_2.id, unit_id=don_vi_hop.id, quantity=23)
        #
        # med3_unit1 = MedicineUnit(medicine_id=thuoc_3.id, unit_id=don_vi_vien.id, quantity=1)
        # med3_unit2 = MedicineUnit(medicine_id=thuoc_3.id, unit_id=don_vi_vi.id, quantity=11)
        #
        # db.session.add_all([med1_unit1, med1_unit2, med1_unit3, med2_unit1, med2_unit2, med3_unit1, med3_unit2])
        # db.session.commit()


        # APPOINTMENT CỦA HUY
#         new_user5 = User(
#             name='Quốc Tuấn',
#         db.create_all()

# new_user = User(
#     name='benh nhan',s
#     phone='0905952379',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='2151013029huy@ou.edu.vn',
#     address='patient Site',
#     username='patient1',
#     password=str(utils.hash_password("123")),
#     gender=Gender.MALE,
#     cid='066203000228',
#     role=UserRole.PATIENT,
# )
# db.session.add_all([new_user])
# db.session.commit()
# new_doctor = Patient(id=new_user.id)
# db.session.add_all([new_doctor])
# db.session.commit()
# new_user = User(
#     name='ADMIN',
#     phone='0905952379',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='voquochuy3006@gmail.com',
#     address='admin Site',
#     username='admin1',
#     password=str(utils.hash_password("123")),
#     gender=Gender.MALE,
#     cid='066203000227',
#     role=UserRole.ADMIN,
# )
# db.session.add_all([new_user])
# db.session.commit()
# new_doctor = Admin(id=new_user.id)
# db.session.add_all([new_doctor])
# db.session.commit()
# new_user = User(
#     name='y ta',
#     phone='0905952379',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='baoempro2003@gmail.com',
#     address='nurse Site',
#     username='nurse1',
#     password=str(utils.hash_password("123")),
#     gender=Gender.MALE,
#     cid='066203000229',
#     role=UserRole.NURSE,
# )
# db.session.add_all([new_user])
# db.session.commit()
# new_doctor = Nurse(id=new_user.id)
# db.session.add_all([new_doctor])
# db.session.commit()
#         new_appointment_list = AppointmentList(
#             scheduled_date=datetime.date(2024, 5, 10),  # Ngày đặt cuộc hẹn
#             nurse_id=3  # ID của y tá (Nurse)
#         )
#
# #         # # Thêm đối tượng mới vào session và lưu xuống cơ sở dữ liệu
#         db.session.add(new_appointment_list)
#         db.session.commit()

#         new_user1 = User(
#             name='Admin',
#             phone='0123456789',
#             avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#             email='admin@example.com',
#             address='Admin Site',
#             username='admin',
#             password=str(utils.hash_password("123")),
#             cid='092884828822',
#             gender=Gender.MALE,
#             role=UserRole.ADMIN,
#         )
#         new_user2 = User(
#             name='Doctor Strange',

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
#         db.session.add_all([new_user1, new_user2, new_user3])
#         db.session.commit()
#         new_doctor = Doctor(id=new_user2.id)
#         new_admin = Admin(id=new_user1.id)
#         new_patient = Patient(id=new_user3.id)
#         db.session.add_all([new_doctor, new_admin, new_patient])
#         db.session.commit()

#         danh_muc_1 = Category(name="Giảm đau")
#         danh_muc_2 = Category(name="Thực phẩm bổ sung")
#         danh_muc_3 = Category(name="Thần Kinh")

#         db.session.add_all([danh_muc_1, danh_muc_2, danh_muc_3])
#         db.session.commit()

#         don_vi_vien = Unit(name="Viên")
#         don_vi_hop = Unit(name="Hộp")
#         don_vi_chai = Unit(name="Chai")

#         db.session.add_all([don_vi_vien, don_vi_hop, don_vi_chai])
#         db.session.commit()

#         # Tạo các loại thuốc (medicine)
#         thuoc_1 = Medicine(name="Panadol", price=10000, usage="Uống sau bữa ăn", exp=datetime.date(2025, 12, 31))
#         thuoc_2 = Medicine(name="Zinc", price=20000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))
#         thuoc_3 = Medicine(name="Vitamin C", price=30000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))

#         db.session.add_all([thuoc_1, thuoc_2, thuoc_3])
#         db.session.commit()

#         cat_med1 = MedicineCategory(category_id=danh_muc_1.id, medicine_id=thuoc_1.id)
#         cat_med2 = MedicineCategory(category_id=danh_muc_2.id, medicine_id=thuoc_1.id)
#         cat_med3 = MedicineCategory(category_id=danh_muc_2.id, medicine_id=thuoc_2.id)
#         cat_med4 = MedicineCategory(category_id=danh_muc_3.id, medicine_id=thuoc_3.id)

#         db.session.add_all([cat_med1, cat_med2, cat_med3, cat_med4])
#         db.session.commit()


# APPOINTMENT CỦA HUY
#         # new_appointment_list = AppointmentList(
#         #     scheduled_date=datetime.date(2024, 4, 25),  # Ngày đặt cuộc hẹn
#         #     nurse_id=1  # ID của y tá (Nurse)
#         # )
#         #
#         # # Thêm đối tượng mới vào session và lưu xuống cơ sở dữ liệu
#         # db.session.add(new_appointment_list)
#         # db.session.commit()
#         new_appointment = Appointment(
#             scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#             scheduled_hour=datetime.time(10, 30),  # Giờ đặt cuộc     hẹn
#             is_confirm=False,  # Trạng thái xác nhận
#             is_paid=False,  # Trạng thái thanh toán
#             status=False,  # Trạng thái cuộc hẹn
#             appointment_list_id= None,  # ID của danh sách đặt hẹn
#             patient_id=2  # ID của bệnh nhân
# =======
#         new_user = User(
# name='Admin',
# phone='0123456789',
# avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
# email='admin@example.com',
# address='Admin Site',
# username='admin',
# password=str(utils.hash_password("123")),
# gender=Gender.MALE,
# role=UserRole.ADMIN,)
#         )
#         db.session.add_all([new_user5, new_user6])
#         db.session.commit()

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
        # new_cashier = Cashier(id=3)
        # db.session.add(new_cashier)
        # db.session.commit()

# new_user5 = User(
#     name='Luu Danh',
#     phone='0123456789',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='cashier123@example.com',
#     address='Clinic',
#     username='nurse',
#     password=str(utils.hash_password("123")),
#     cid='23498423189',
#     gender=Gender.MALE,
#     role=UserRole.NURSE,
# )
# db.session.add(new_user5)
# db.session.commit()
# new_nurse = Nurse(id=new_user5.id)
# db.session.add(new_nurse)
# db.session.commit()

# new_appointment_list = AppointmentList(
#     scheduled_date=datetime.date(2024, 4, 25),  # Ngày đặt cuộc hẹn
#     nurse_id=7  # ID của y tá (Nurse)
# )
#
# db.session.add(new_appointment_list)
# db.session.commit()

# new_appointment = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(15, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=2,  # ID của danh sách đặt hẹn
#     patient_id=1  # ID của bệnh nhân
# )
# new_appointment2 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(16, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=2,  # ID của danh sách đặt hẹn
#     patient_id=1  # ID của bệnh nhân
# )
# new_appointment3 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(8, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=2,  # ID của danh sách đặt hẹn
#     patient_id=1  # ID của bệnh nhân
# )
# new_appointment4 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=2,  # ID của danh sách đặt hẹn
#     patient_id=1  # ID của bệnh nhân
# )
# new_appointment5 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(11, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=2,  # ID của danh sách đặt hẹn
#     patient_id=1  # ID của bệnh nhân
# )
# db.session.add_all([
#     new_appointment,
#     new_appointment2,
#     new_appointment3,
#     new_appointment4,
#     new_appointment5
# ])
# db.session.commit()

# new_appointment_list = AppointmentList(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     nurse_id=7  # ID của y tá (Nurse)
# )
#
# db.session.add(new_appointment_list)
# db.session.commit()
#
# new_appointment = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(15, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=new_appointment_list.id,  # ID của danh sách đặt hẹn
#     patient_id=5  # ID của bệnh nhân
# )
# new_appointment2 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(16, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=new_appointment_list.id,  # ID của danh sách đặt hẹn
#     patient_id=5  # ID của bệnh nhân
# )
# new_appointment3 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(8, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=new_appointment_list.id,  # ID của danh sách đặt hẹn
#     patient_id=5  # ID của bệnh nhân
# )
# new_appointment4 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=new_appointment_list.id,  # ID của danh sách đặt hẹn
#     patient_id=5  # ID của bệnh nhân
# )
# new_appointment5 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(11, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=new_appointment_list.id,  # ID của danh sách đặt hẹn
#     patient_id=5  # ID của bệnh nhân
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

# new_prescription2 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=1,
#     appointment_id=2
#
# )
# new_prescription3 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=1,
#     appointment_id=3
#
# )
# new_prescription4 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=1,
#     appointment_id=4
#
# )
# new_prescription5 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=1,
#     appointment_id=5
#
# )
# new_prescription6 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=1,
#     appointment_id=6
#
# )
# new_prescription7 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=5,
#     appointment_id=7
#
# )
# new_prescription8 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=6,
#     appointment_id=8
#
# )
# new_prescription9 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=6,
#     appointment_id=9
#
# )
# new_prescription10 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=5,
#     appointment_id=10
#
# )
# new_prescription11 = Prescription(
#     date=datetime.date(2024, 4, 25),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=8,
#     patient_id=6,
#     appointment_id=11
#
# )
# db.session.add_all([
#     new_prescription2,
#     new_prescription3,
#     new_prescription4,
#     new_prescription5,
#     new_prescription6,
#     new_prescription7,
#     new_prescription8,
#     new_prescription9,
#     new_prescription10,
#     new_prescription11,
#
# ])
# db.session.commit()

# SETUP DB LAI TU DAU
# cashier = User(
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
# db.session.add(cashier)
# db.session.commit()
# new_cashier = Cashier(id=cashier.id)
# db.session.add(new_cashier)
# db.session.commit()
#
# quoctuan = User(
#     name='Quốc Tuấn',
#     phone='0123456789',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='patient2@example.com',
#     address='Clinic',
#     username='patient2',
#     password=str(utils.hash_password("123")),
#     cid='2654894321',
#     gender=Gender.MALE,
#     role=UserRole.PATIENT,
# )
# anhtuan = User(
#     name='Anh Tuấn',
#     phone='0123456789',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='patient3@example.com',
#     address='Clinic',
#     username='patient3',
#     password=str(utils.hash_password("123")),
#     cid='32589441528',
#     gender=Gender.MALE,
#     role=UserRole.PATIENT,
# )
# db.session.add_all([quoctuan, anhtuan])
# db.session.commit()
# new_quoctuan = Patient(id=quoctuan.id)
# new_anhtuan = Patient(id=anhtuan.id)
# db.session.add_all([new_quoctuan, new_anhtuan])
# db.session.commit()
#
# doctor = User(
#     name='Doctor Strange',
#     phone='0123456789',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='docter@example.com',
#     address='Clinic',
#     username='doctorstrange',
#     password=str(utils.hash_password("123")),
#     cid='092884828872',
#     gender=Gender.MALE,
#     role=UserRole.DOCTOR,
# )
# db.session.add_all([doctor])
# db.session.commit()
# new_doctor = Doctor(id=doctor.id)
# db.session.add_all([new_doctor])
# db.session.commit()
# luudanh = User(
#     name='Luu Danh',
#     phone='0123456789',
#     avatar='https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg',
#     email='cashier123@example.com',
#     address='Clinic',
#     username='nurse',
#     password=str(utils.hash_password("123")),
#     cid='23498423189',
#     gender=Gender.MALE,
#     role=UserRole.NURSE,
# )
# db.session.add(luudanh)
# db.session.commit()
# new_nurse = Nurse(id=luudanh.id)
# db.session.add(new_nurse)
# db.session.commit()
# thuocho = Category(
#     name='Thuốc Ho'
# )
# thuoccam = Category(
#     name='Thuốc Cảm'
# )
# thucphamchucnang = Category(
#     name='Thực Phẩm Chức Năng'
# )
# thuocgiamdau = Category(
#     name='Thuốc Giảm Đau'
# )
# db.session.add_all([thuocgiamdau, thuocho, thuoccam])
# db.session.add_all([thucphamchucnang])
# db.session.commit()
# Tạo các loại thuốc (medicine)
# thuoc_1 = Medicine(name="Panadol", price=10000, usage="Uống sau bữa ăn", exp=datetime.date(2025, 12, 31))
# thuoc_2 = Medicine(name="Zinc", price=20000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))
# thuoc_3 = Medicine(name="Vitamin C", price=30000, usage="Uống trước khi ngủ", exp=datetime.date(2024, 6, 30))

# db.session.add_all([thuoc_1, thuoc_2, thuoc_3])
# db.session.commit()
# cat_med1 = MedicineCategory(category_id=3, medicine_id=1)
# cat_med2 = MedicineCategory(category_id=1, medicine_id=1)
# cat_med3 = MedicineCategory(category_id=4, medicine_id=2)
# cat_med4 = MedicineCategory(category_id=4, medicine_id=3)
#
# db.session.add_all([cat_med1, cat_med2, cat_med3, cat_med4])
# db.session.commit()

# unit1 = Unit(name='vỉ')
# unit2 = Unit(name='chai')
# unit3 = Unit(name='viên')
# db.session.add_all([unit1, unit2, unit3])
# db.session.commit()

# medicine_unit1 = MedicineUnit(
#     unit_id=1,
#     medicine_id=1,
#     quantity=10
# )
# medicine_unit2 = MedicineUnit(
#     unit_id=3,
#     medicine_id=1,
#     quantity=1
# )
# medicine_unit3 = MedicineUnit(
#     unit_id=2,
#     medicine_id=2,
#     quantity=30
# )
# medicine_unit4 = MedicineUnit(
#     unit_id=1,
#     medicine_id=2,
#     quantity=8
# )
# medicine_unit5 = MedicineUnit(
#     unit_id=1,
#     medicine_id=2,
#     quantity=14
# )
# db.session.add_all([medicine_unit5, medicine_unit4, medicine_unit3, medicine_unit1, medicine_unit2])
# db.session.commit()

# new_appointment_list = AppointmentList(
#     scheduled_date=datetime.date(2024, 4, 25),  # Ngày đặt cuộc hẹn
#     nurse_id=5  # ID của y tá (Nurse)
# )
#
# db.session.add(new_appointment_list)
# db.session.commit()

# new_appointment = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(15, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=1,  # ID của danh sách đặt hẹn
#     patient_id=2  # ID của bệnh nhân
# )
# new_appointment2 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(16, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=1,  # ID của danh sách đặt hẹn
#     patient_id=2  # ID của bệnh nhân
# )
# new_appointment3 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(8, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=1,  # ID của danh sách đặt hẹn
#     patient_id=2  # ID của bệnh nhân
# )
# new_appointment4 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(9, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=1,  # ID của danh sách đặt hẹn
#     patient_id=2  # ID của bệnh nhân
# )
# new_appointment5 = Appointment(
#     scheduled_date=datetime.date(2024, 4, 30),  # Ngày đặt cuộc hẹn
#     scheduled_hour=datetime.time(11, 30),  # Giờ đặt cuộc hẹn
#     is_confirm=False,  # Trạng thái xác nhận
#     is_paid=False,  # Trạng thái thanh toán
#     status=True,  # Trạng thái cuộc hẹn
#     appointment_list_id=1,  # ID của danh sách đặt hẹn
#     patient_id=2  # ID của bệnh nhân
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

# new_prescription2 = Prescription(
#     date=datetime.date(2024, 4, 30),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=4,
#     patient_id=2,
#     appointment_id=2
#
# )
# new_prescription3 = Prescription(
#     date=datetime.date(2024, 4, 30),
#     symptoms="Ho sổ mũi nhiều đờm",
#     diagnosis='Cảm cúm',
#     doctor_id=4,
#     patient_id=2,
#     appointment_id=1
#
# )
# db.session.add_all([new_prescription3, new_prescription2])
# db.session.commit()

# medicine_detail = MedicineDetail(
#     quantity=2,
#     usage="2 lần/ngày, sáng chiều",
#     prescription_id=1,
#     medicine_id=1,
#     medicine_unit_id=1
# )
# medicine_detail2 = MedicineDetail(
#     quantity=2,
#     usage="2 lần/ngày, sáng chiều",
#     prescription_id=1,
#     medicine_id=3,
#     medicine_unit_id=1
# )
# medicine_detail3 = MedicineDetail(
#     quantity=1,
#     usage="2 lần/ngày, sáng chiều",
#     prescription_id=1,
#     medicine_id=2,
#     medicine_unit_id=2
# )
# db.session.add_all([medicine_detail2, medicine_detail, medicine_detail3])
# db.session.commit()
