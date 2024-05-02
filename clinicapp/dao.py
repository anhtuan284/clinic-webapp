import hashlib

from sqlalchemy.orm import sessionmaker

from clinicapp import db
from clinicapp.models import User, UserRole, Medicine, Category, MedicineCategory, Unit, Prescription, MedicineDetail
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
    u = User(ten=name, username=username, password=hashed_password, avatar=avatar, role=UserRole.PATIENT)
    db.session.add(u)
    db.session.commit()


def get_medicines(price_bat_dau=None, price_ket_thuc=None, han_dung_bat_dau=None, han_dung_ket_thuc=None, name=None, category_id=None):
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

    print(medicines)

    return medicines


def get_medicine_by_id(id):
    return Medicine.query.get(id)


def get_medicine_current_category(category_id):
    medicines = db.session.query(Medicine, Category, MedicineCategory) \
        .filter(Medicine.id == MedicineCategory.medicine_id, MedicineCategory.category_id == Category.id) \
        .filter(Category.id == category_id) \
        .all()

    return medicines


def delete_medicine_by_id(id):
    delete_all_category_medicine_by_medicine_id(id)
    db.session.query(Medicine).filter(Medicine.id == id).delete()
    db.session.commit()


def add_or_update_medicine(id, price, name, usage, exp):
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


def get_categorys():
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


def get_categorys_current_medicine(id):
    categorymedicine = db.session.query(Medicine, Category, MedicineCategory) \
        .filter(Medicine.id == MedicineCategory.medicine_id, MedicineCategory.category_id == Category.id) \
        .filter(Medicine.id == id) \
        .all()

    print(categorymedicine)
    return categorymedicine


def get_units():
    return db.session.query(Unit).all()


def update_list_appointment(patient_id):
    return None


def create_medical_form(doctor_id, patient_id, date, diagnosis, symptoms, usages, quantities, medicines, units):
    new_pres = Prescription(date=date, diagnosis=diagnosis, symptoms=symptoms, patient_id=patient_id, doctor_id=doctor_id)
    db.session.add(new_pres)
    db.session.commit()
    print(usages)
    print(quantities)
    print(medicines)
    print(units)
    print(new_pres.id)
    for i in range(len(medicines)):
        medicine_id = medicines[i]
        quantity = quantities[i]
        usage = usages[i]
        unit = units[i]
        medicine_detail = MedicineDetail(medicine_id=medicine_id, unit_id=unit, quantity=quantity, usage=usage, prescription_id=new_pres.id)
        db.session.add(medicine_detail)
    db.session.commit()
