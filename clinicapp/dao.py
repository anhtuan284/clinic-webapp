import hashlib

from sqlalchemy import func, desc
from sqlalchemy.orm import sessionmaker

from clinicapp import db
from clinicapp.models import *

from clinicapp.utils import hash_password, verify_password


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    user = User.query.filter_by(username=username.strip()).first()
    if user and verify_password(password.strip(), user.password):
        return user
    return None


def add_user(name, username, password, avatar, email, phone, address, cid, gender):
    hashed_password = hash_password(password.strip())
    u = User(
        username=username,
        password=hashed_password,
        role=UserRole.PATIENT,
        name=name,
        cid=cid,
        phone=phone,
        email=email,
        gender=gender,
        address=address,
        avatar=avatar
    )
    db.session.add(u)
    db.session.commit()
    new_patient = Patient(id=u.id)
    db.session.add(new_patient)
    db.session.commit()


def get_quantity_appointment_by_date(date):
    quantity = Appointment.query.filter_by(scheduled_date=date, is_confirm=False).count()
    return quantity


def get_list_scheduled_hours_by_date_no_confirm(date):
    appointments = Appointment.query.filter_by(scheduled_date=date).with_entities(Appointment.scheduled_hour).all()
    scheduled_hours = [appointment.scheduled_hour for appointment in appointments]
    # print(scheduled_hours)
    return scheduled_hours


def get_list_scheduled_hours_by_date_confirm(date):
    appointments = Appointment.query.filter_by(scheduled_date=date, is_confirm=True).with_entities(
        Appointment.scheduled_hour).all()
    scheduled_hours = [appointment.scheduled_hour for appointment in appointments]
    # print(scheduled_hours)
    return scheduled_hours


def add_appointment(scheduled_date, scheduled_hour, is_confirm, is_paid, status, patient_id):
    appoinment = Appointment(scheduled_date=scheduled_date, scheduled_hour=scheduled_hour, is_confirm=is_confirm,
                             is_paid=is_paid, status=status, patient_id=patient_id)
    db.session.add(appoinment)
    db.session.commit()


def get_medicines(price_bat_dau=None, price_ket_thuc=None, han_dung_bat_dau=None, han_dung_ket_thuc=None, name=None,
                  category_id=None):
    medicines = Medicine.query

    if category_id:
        medicines = medicines.join(Medicine.medicine_category).filter_by(category_id=category_id)

    if price_bat_dau:
        medicines = medicines.filter(Medicine.price >= price_bat_dau)

    if price_ket_thuc:
        medicines = medicines.filter(Medicine.price <= price_ket_thuc)

    if han_dung_bat_dau:
        medicines = medicines.filter(Medicine.exp >= han_dung_bat_dau)

    if han_dung_ket_thuc:
        medicines = medicines.filter(Medicine.exp <= han_dung_ket_thuc)

    if name:
        medicines = medicines.filter(Medicine.name.contains(name))

    medicines = medicines.all()

    return medicines


def get_medicine_by_id(id):
    return Medicine.query.get(id)


def get_medicine_by_category(category_id):
    medicines = db.session.query(Medicine).join(Medicine.medicine_category).filter(
        MedicineCategory.category_id == category_id).all()

    return medicines


def delete_medicine_by_id(id):
    delete_all_category_medicine_by_medicine_id(id)
    db.session.query(Medicine).filter(Medicine.id == id).delete()
    db.session.commit()


def add_or_update_medicine(id: object, price: object, name: object, usage: object, exp: object) -> object:
    if id:
        medicine = get_medicine_by_id(id)
        medicine.price = price
        medicine.name = name
        medicine.usage = usage
        medicine.exp = exp
        db.session.commit()
        return medicine.id
    else:
        medicineMoi = Medicine(
            price=price,
            name=name,
            usage=usage,
            exp=exp
        )
        db.session.add(medicineMoi)
        db.session.commit()
        return medicineMoi.id


def get_categories():
    return db.session.query(Category).all()


def get_category_medicines():
    return MedicineCategory.query.all()


def get_category_medicine_by_category_va_medicine(category_id, medicine_id):
    return MedicineCategory.query.filter_by(category_id=category_id, medicine_id=medicine_id).all()


def delete_all_category_medicine_by_medicine_id(medicine_id):
    db.session.query(MedicineCategory).filter(MedicineCategory.medicine_id == medicine_id).delete()
    db.session.commit()


def add_category_medicine(category_id, medicine_id):
    if get_category_medicine_by_category_va_medicine(category_id, medicine_id):
        return

    danhMucMedicineMoi = MedicineCategory(
        category_id=category_id,
        medicine_id=medicine_id
    )
    db.session.add(danhMucMedicineMoi)
    db.session.commit()


def get_categories_by_medicine_id(id):
    categories = Category.query.join(Category.medicine_category).filter_by(medicine_id=id).all()

    return categories


def get_value_policy(id):
    policy = Policy.query.get(id)
    if policy:
        return policy.value
    else:
        return None


def get_units():
    return db.session.query(Unit).all()


def update_list_appointment(patient_id):
    return None


def create_prescription(doctor_id, patient_id, date, diagnosis, symptoms, usages, quantities, medicines, units):
    new_pres = Prescription(date=date, diagnosis=diagnosis, symptoms=symptoms, patient_id=patient_id,
                            doctor_id=doctor_id)

    db.session.add(new_pres)
    db.session.commit()
    for i in range(len(medicines)):
        medicine_id = medicines[i]
        quantity = quantities[i]
        usage = usages[i]
        unit = units[i]
        medicine_detail = MedicineDetail(medicine_id=medicine_id, unit_id=unit, quantity=quantity, usage=usage,
                                         prescription_id=new_pres.id)
        db.session.add(medicine_detail)
    db.session.commit()


def create_order_payment(amount, gateway, patient_id, paid, response_code):
    order = HistoryOnlinePayment(amount=amount, gateway_name=gateway, patient_id=patient_id, paid=paid,
                                 response_code=response_code)
    db.session.add(order)
    db.session.commit()


def get_quantity_history_payment():
    latest_record = HistoryOnlinePayment.query.order_by(desc(HistoryOnlinePayment.id)).first()
    if latest_record.id:
        return latest_record.id
    else:
        return 1


def get_prescriptions_by_scheduled_date(date):
    prescriptions = db.session.query(Prescription, Appointment, AppointmentList) \
        .filter(Prescription.appointment_id == Appointment.id) \
        .filter(Appointment.appointment_list_id == AppointmentList.id) \
        .filter(AppointmentList.scheduled_date == date) \
        .all()

    return prescriptions


def get_prescription_by_id(prescription_id):
    prescription = Prescription.query.get(prescription_id)

    return prescription


def get_patient_by_prescription_id(prescription_id):
    patient = User.query.get(get_prescription_by_id(prescription_id).patient_id)

    return patient


def get_medicines_by_prescription_id(prescription_id):
    medicines = db.session.query(MedicineDetail, Medicine, MedicineUnit, Unit) \
        .filter(MedicineDetail.medicine_unit_id == MedicineUnit.id) \
        .filter(MedicineUnit.medicine_id == Medicine.id) \
        .filter(MedicineUnit.unit_id == Unit.id) \
        .filter(MedicineDetail.prescription_id == prescription_id) \
        .all()

    return medicines


def get_unit_by_name(name):
    return Unit.query.filter_by(name='vỉ').all()[0]


def get_medicine_price_by_prescription_id(prescription_id):
    total = db.session.query(func.sum(MedicineDetail.quantity * MedicineUnit.quantity * Medicine.price)) \
        .filter(MedicineUnit.id == MedicineDetail.medicine_unit_id) \
        .filter(MedicineUnit.medicine_id == Medicine.id) \
        .filter(MedicineUnit.unit_id == Unit.id) \
        .filter(MedicineDetail.prescription_id == prescription_id)

    total = total[0][0]
    if not total:
        total = '0'

    return float(str(total))


def get_is_paid_by_prescription_id(prescription_id):
    return Appointment.query.filter_by(id=prescription_id).all()[0].is_paid


def create_bill(service_price, medicine_price, total, cashier_id, prescription_id):
    new_bill = Bill(
        service_price=service_price,
        medicine_price=medicine_price,
        total=total,
        cashier_id=cashier_id,
        prescription_id=prescription_id
    )
    db.session.add(new_bill)
    db.session.commit()


def get_bill_by_prescription_id(prescription_id):
    return Bill.query.filter_by(prescription_id=prescription_id).all()


def get_patient_info(patient_cid=None):
    if patient_cid:
        patient = db.session.query(User).filter_by(cid=patient_cid).first()
        return patient
    return None
