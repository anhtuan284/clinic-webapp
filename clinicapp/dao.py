

from sqlalchemy import func, desc, update, distinct, extract, select, join, and_, asc
import pytz
from sqlalchemy.orm import sessionmaker, joinedload

from clinicapp import TIENKHAM
from clinicapp.models import *

from clinicapp.utils import hash_password, verify_password, datetime_now_vn


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def auth_user(username, password):
    user = User.query.filter_by(username=username.strip()).first()
    if user and verify_password(password.strip(), user.password):
        return user
    return None


def add_user(name, username, password, avatar, email, phone, address, cid, gender, dob):
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
        avatar=avatar,
        dob=dob
    )
    db.session.add(u)
    db.session.commit()
    new_patient = Patient(id=u.id)
    db.session.add(new_patient)
    db.session.commit()


def get_quantity_appointment_by_date(date):
    quantity = Appointment.query.filter_by(scheduled_date=date, is_confirm=True).count()
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
    if category_id == 0:
        return db.session.query(Medicine).all()
    return db.session.query(Medicine).join(Medicine.medicine_category).filter(
        MedicineCategory.category_id == category_id).all()


def delete_medicine_by_id(id):
    delete_all_category_medicine_by_medicine_id(id)
    db.session.query(Medicine).filter(Medicine.id == id).delete()
    db.session.commit()


def add_or_update_medicine(id: object, price: object, name: object, usage: object, exp: object,
                           dict_quantity_per_unit: dict) -> object:
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

        for key in dict_quantity_per_unit.keys():
            if dict_quantity_per_unit[key]:
                mu = MedicineUnit(
                    unit_id=key,
                    medicine_id=medicineMoi.id,
                    quantity=dict_quantity_per_unit[key]
                )
                db.session.add(mu)
        db.session.commit()

        return medicineMoi.id


def get_categories():
    return db.session.query(Category).all()


def get_category_medicines():
    return MedicineCategory.query.all()


def get_medicine_unit_by_medicine_id(medicine_id):
    return MedicineUnit.query.filter_by(medicine_id=medicine_id).all()


def get_category_medicine_by_category_va_medicine(category_id, medicine_id):
    return MedicineCategory.query.filter_by(category_id=category_id, medicine_id=medicine_id).all()


def get_medicine_unit_by_unit_va_medicine(unit_id, medicine_id):
    return MedicineUnit.query.filter_by(unit_id=unit_id, medicine_id=medicine_id).all()


def delete_all_category_medicine_by_medicine_id(medicine_id):
    db.session.query(MedicineCategory).filter(MedicineCategory.medicine_id == medicine_id).delete()
    db.session.commit()


def delete_all_medicine_unit_by_medicine_id(medicine_id):
    db.session.query(MedicineUnit).filter(MedicineUnit.medicine_id == medicine_id).delete()
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


def add_medicine_unit(unit_id, medicine_id, quantity):
    if get_medicine_unit_by_unit_va_medicine(unit_id, medicine_id):
        return

    medicineUniteMoi = MedicineUnit(
        unit_id=unit_id,
        medicine_id=medicine_id,
        quantity=quantity
    )
    db.session.add(medicineUniteMoi)
    db.session.commit()


def get_categories_by_medicine_id(medicine_id):
    categories = Category.query.join(Category.medicine_category).filter_by(medicine_id=medicine_id).all()

    return categories


def get_unit_name_and_quantity():
    return db.session.query(Unit.name, MedicineUnit.quantity, MedicineUnit.medicine_id) \
        .filter(MedicineUnit.unit_id == Unit.id) \
        .all()


def get_unit_by_medicine_id(medicine_id):
    return Unit.query.join(MedicineUnit, MedicineUnit.unit_id == Unit.id).filter(
        MedicineUnit.medicine_id == medicine_id).all()


def get_medicine_unit():
    return MedicineUnit.query.all()


def get_value_policy(id):
    policy = Policy.query.get(id)
    if policy:
        return policy.value
    else:
        return None


def get_policy_value_by_name(name):
    policy = Policy.query.filter_by(name=name).all()
    if policy:
        return float(policy[0].value)
    else:
        return None


def get_units():
    return db.session.query(Unit).all()


def get_unit_by_id(id):
    unit = db.session.query(Unit).get(id)
    return unit.name


def get_units_by_medicine(medicine_id):
    return db.session.query(MedicineUnit).filter_by(medicine_id=medicine_id).all()


def create_prescription(doctor_id, patient_id, date, diagnosis, symptoms, usages, quantities, medicines,
                        medicine_units, appointment_id):
    new_pres = Prescription(date=date, diagnosis=diagnosis, symptoms=symptoms, patient_id=patient_id,
                            doctor_id=doctor_id, appointment_id=appointment_id)
    db.session.add(new_pres)
    db.session.commit()
    for i in range(len(medicines)):
        medicine_id = medicines[i]
        quantity = quantities[i]
        usage = usages[i]
        medicine_unit = medicine_units[i]
        medicine_detail = MedicineDetail(medicine_id=medicine_id, medicine_unit_id=medicine_unit, quantity=quantity,
                                         usage=usage,
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


def get_unpaid_prescriptions(scheduled_date):
    prescriptions = db.session.query(Prescription, Appointment) \
        .filter(Prescription.appointment_id == Appointment.id) \
        .filter(Prescription.id.notin_(db.session.query(Bill.prescription_id)))

    if scheduled_date:
        prescriptions = prescriptions.filter(Appointment.scheduled_date == scheduled_date)
    print(prescriptions.all())
    return prescriptions.all()


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
    total = db.session.query(func.sum(MedicineDetail.quantity * MedicineUnit.quantity * Medicine.price).label('sum')) \
        .filter(MedicineUnit.id == MedicineDetail.medicine_unit_id) \
        .filter(MedicineDetail.prescription_id == prescription_id) \
        .filter(MedicineDetail.medicine_id == Medicine.id)

    total = total[0].sum
    if not total:
        total = '0'

    return float(str(total))


def get_is_paid_by_prescription_id(prescription_id):
    # Assuming Prescription and Appointment are SQLAlchemy model classes
    queryList = db.session.query(Appointment.id, Prescription.id, Appointment.is_paid) \
        .filter(Appointment.id == Prescription.appointment_id) \
        .filter(Prescription.id == prescription_id) \
        .first()

    print(queryList)

    return queryList[2]


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


def get_patient_info(patient_cid=None, scheduled_date=None):
    if patient_cid and scheduled_date:
        patient = db.session.query(User.name, User.id, User.phone, User.email, Appointment.id) \
            .filter(User.id == Appointment.patient_id) \
            .filter(Appointment.scheduled_date == scheduled_date, Appointment.status == True) \
            .filter(User.cid == patient_cid).first()

        print(patient)

        return patient
    return None


# def get_patient_info(patient_cid=None, scheduled_date=None):
#     if patient_cid and scheduled_date:
#         patient = db.session.query(User)\
#             .join(Appointment, User.id == Appointment.patient_id)\
#             .filter(User.cid == patient_cid, Appointment.scheduled_date == scheduled_date, Appointment.status == True)\
#             .first()
#         return patient
#     return None

def get_list_appointment_no_confirm_by_date(date):
    if date is not None:
        appointments_with_patient_info = db.session.query(Appointment, User). \
            join(User, User.id == Appointment.patient_id). \
            filter(Appointment.is_confirm == False, scheduled_date=date).all()
    else:
        appointments_with_patient_info = db.session.query(Appointment, User). \
            join(User, User.id == Appointment.patient_id). \
            filter(Appointment.is_confirm == False).all()

    return appointments_with_patient_info


def get_list_appointment_confirm_by_date(date):
    if date is not None:
        appointments_with_patient_info = db.session.query(Appointment, User). \
            join(User, User.id == Appointment.patient_id). \
            filter(Appointment.is_confirm == True, Appointment.status == False, scheduled_date=date).all()
    else:
        appointments_with_patient_info = db.session.query(Appointment, User). \
            join(User, User.id == Appointment.patient_id). \
            filter(Appointment.is_confirm == True, Appointment.status == False).all()
    return appointments_with_patient_info


def get_appointment_by_id(id):
    return Appointment.query.get(id)


def update_confirm_appointment(id):
    appointment = get_appointment_by_id(id)
    if appointment:
        appointment.is_confirm = True
        db.session.commit()


def conflict_appointment(scheduled_date, scheduled_hour):
    conflicting_appointments = Appointment.query.filter_by(scheduled_date=scheduled_date, scheduled_hour=scheduled_hour,
                                                           is_confirm=True).all()
    if conflicting_appointments:
        return True
    else:
        return False


def delete_appointment(appointment):
    # try:
    #     db.session.delete(appointment)
    #     db.session.commit()
    # except Exception as e:
    #     # Handle exceptions if any
    #     db.session.rollback()
    #     raise e
    db.session.delete(appointment)
    db.session.commit()


def get_date_range():
    current_date = datetime.datetime.now().date()
    nearest_date = db.session.query(func.max(AppointmentList.scheduled_date)).scalar()
    if not nearest_date:
        nearest_date = current_date
    date_range = db.session.query(AppointmentList.scheduled_date) \
        .filter(AppointmentList.scheduled_date >= current_date, AppointmentList.scheduled_date <= nearest_date) \
        .order_by(AppointmentList.scheduled_date) \
        .all()
    date_range = [date[0] for date in date_range]
    return date_range


def get_approved_appointments_by_date(date):
    approved_appointments = (db.session.query(Appointment, User)
                             .filter(Appointment.patient_id == User.id)
                             .filter(Appointment.status)
                             .filter(Appointment.scheduled_date == date)
                             .filter(Appointment.prescription == None)
                             .order_by(Appointment.scheduled_date, asc(Appointment.scheduled_hour))
                             .all())
    return approved_appointments


def get_prescription_by_patient(patient_id, page=None, start_date=None, diagnosis=None):
    q = Prescription.query.filter_by(patient_id=patient_id)
    if start_date:
        q = q.filter(Prescription.date >= start_date)

    if diagnosis:
        q = q.filter(Prescription.diagnosis.contains(diagnosis))

    count_record = q.count()

    if page:
        page_size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * page_size
        q = q.slice(start, start + page_size)

    return q.all(), count_record


def get_patient_by_id(patient_id):
    return db.session.query(Patient).get(patient_id)


def get_doctor_by_id(doctor_id):
    return User.query.get(id=doctor_id)


def get_patient_obj_by_id(patient_id):
    return User.query.get(id=patient_id)


def get_all_doctor():
    return User.query.filter_by(role=UserRole.DOCTOR).all()


def get_all_patient():
    return User.query.filter_by(role=UserRole.PATIENT).all()


def get_appointment_booked_by_patient_id(patient_id):
    vn_time = datetime_now_vn()
    # current_datetime = datetime.datetime.now()
    current_date = vn_time.date()
    current_time = vn_time.time()

    return Appointment.query.filter(
        Appointment.patient_id == patient_id,
        (Appointment.scheduled_date == current_date) &
        (Appointment.scheduled_hour >= current_time) |
        (Appointment.scheduled_date > current_date)
    ).first()


def make_the_list(card_data):
    appointment_ids = [int(card['appointment_id']) for card in card_data]
    db.session.execute(update(Appointment).where(Appointment.id.in_(appointment_ids)).values(status=True))
    for card in card_data:
        appointment_id = int(card['appointment_id'])
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            scheduled_date = appointment.scheduled_date
            appointment_list = AppointmentList.query.filter_by(scheduled_date=scheduled_date).first()
            if appointment_list:
                appointment.appointment_list_id = appointment_list.id
    db.session.commit()


def get_patient_by_cid(patient_cid):
    user = User.query.filter_by(cid=patient_cid).first()
    return user


def delete_patient_by_id(patient_id):
    Patient.query.filter_by(id=patient_id).delete()
    db.session.commit()


def delete_admin_by_id(admin_id):
    Admin.query.filter_by(id=admin_id).delete()
    db.session.commit()


def delete_doctor_by_id(doctor_id):
    Doctor.query.filter_by(id=doctor_id).delete()
    db.session.commit()


def delete_nurse_by_id(nurse_id):
    Nurse.query.filter_by(id=nurse_id).delete()
    db.session.commit()


def delete_cashier_by_id(cashier_id):
    Cashier.query.filter_by(id=cashier_id).delete()
    db.session.commit()


def get_revenue_percentage_stats(month_str):
    # Chuyển chuỗi thành đối tượng datetime
    date_object = datetime.datetime.strptime(month_str, "%Y-%m")

    # Lấy năm và tháng từ đối tượng datetime
    year = date_object.year
    month = date_object.month

    # danh sach tong tien thuoc moi prescription-co-thuoc theo thang
    month_medicine_revenue_by_drug_assigned_prescription = \
        db.session.query(extract('month', Prescription.date).label("month"),
                         extract('year', Prescription.date).label("year"), Prescription.id,
                         func.sum(MedicineDetail.quantity * MedicineUnit.quantity * Medicine.price).label(
                             "total_month_medicine_revenue")) \
            .filter(MedicineDetail.medicine_id.__eq__(Medicine.id)) \
            .filter(MedicineDetail.prescription_id.__eq__(Prescription.id)) \
            .filter(MedicineDetail.medicine_unit_id.__eq__(MedicineUnit.id)) \
            .filter(extract('month', Prescription.date) == month) \
            .filter(extract('year', Prescription.date) == year) \
            .group_by(extract('month', Prescription.date)) \
            .group_by(extract('year', Prescription.date)) \
            .group_by(Prescription.id).all()

    # tong-tien-cac-prescription-co-thuoc theo thang
    month_revenue_by_drug_assigned_prescription = 0
    for item in month_medicine_revenue_by_drug_assigned_prescription:
        month_revenue_by_drug_assigned_prescription += item.total_month_medicine_revenue + 100000

    # so prescription khong co thuoc theo thang
    drugless_prescription_by_month_count = db.session.query(func.count(Prescription.id)).filter(
        Prescription.id.notin_(db.session.query(MedicineDetail.prescription_id))
    ).filter(extract('month', Prescription.date) == month) \
        .filter(extract('year', Prescription.date) == year).all()
    print(drugless_prescription_by_month_count)

    # tong-tien-kham cac-prescription-ko-thuoc theo thang
    month_revenue_by_drugless_prescription = drugless_prescription_by_month_count[0][0] * 100000

    # tong-tien theo thang
    month_revenue = month_revenue_by_drugless_prescription + month_revenue_by_drug_assigned_prescription
    print(month_revenue)

    # danh sach tong tien thuoc cac prescription-co-thuoc theo ngay
    date_medicine_revenue_by_drug_assigned_prescription = \
        db.session.query(Prescription.date, func.count(distinct(Patient.id)).label('patient_count'),
                         (func.sum(MedicineDetail.quantity * MedicineUnit.quantity * Medicine.price)).label(
                             "total_date_medicine_revenue"), (100 * ((func.sum(
                MedicineDetail.quantity * MedicineUnit.quantity * Medicine.price)) / month_revenue)).label(
                'percentage')) \
            .filter(Prescription.patient_id == Patient.id) \
            .filter(MedicineDetail.medicine_id.__eq__(Medicine.id)) \
            .filter(MedicineDetail.prescription_id.__eq__(Prescription.id)) \
            .filter(MedicineDetail.medicine_unit_id.__eq__(MedicineUnit.id)) \
            .filter(extract('month', Prescription.date) == month) \
            .filter(extract('year', Prescription.date) == year) \
            .group_by(Prescription.date).all()
    print(date_medicine_revenue_by_drug_assigned_prescription)

    # danh sach tong tien kham  cac prescription theo ngay
    date_revenue_by_drugless_prescription = \
        db.session.query(Prescription.date,
                         (func.sum(get_value_policy(TIENKHAM))).label(
                             "total_date_revenue"),
                         (100 * (func.sum(get_value_policy(TIENKHAM)) / month_revenue)).label('percentage')) \
            .filter(extract('month', Prescription.date) == month) \
            .filter(extract('year', Prescription.date) == year) \
            .group_by(Prescription.date).all()

    print(date_revenue_by_drugless_prescription[0])

    date_medicine_revenue_by_drug_assigned_prescription_list = []
    for row in date_medicine_revenue_by_drug_assigned_prescription:
        date_medicine_revenue_by_drug_assigned_prescription_list.append({
            'prescription_date': row[0],
            'patient_count': row.patient_count,
            "total_date_medicine_revenue": row.total_date_medicine_revenue,
            "percentage": row.percentage
        })
    print(date_medicine_revenue_by_drug_assigned_prescription_list)

    date_revenue_by_drugless_prescription_list = []
    for row in date_revenue_by_drugless_prescription:
        date_revenue_by_drugless_prescription_list.append({
            'prescription_date': row[0],
            'total_date_revenue': row.total_date_revenue,
            "percentage": row.percentage
        })
    print(date_revenue_by_drugless_prescription_list)

    return [
        date_medicine_revenue_by_drug_assigned_prescription_list,
        date_revenue_by_drugless_prescription_list
    ]

def count_prescription_by_patient(patient_id):
    return Prescription.query.filter(Prescription.patient_id == patient_id).count()


if __name__ == '__main__':
    with app.app_context():
        print(count_prescription_by_patient(patient_id=2))


