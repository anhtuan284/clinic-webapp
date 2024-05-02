from datetime import datetime

import cloudinary.uploader
from flask import request, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required, current_user

from clinicapp import app, dao, login
from clinicapp.decorators import loggedin, roles_required
from clinicapp.forms import PrescriptionForm
from clinicapp.models import UserRole, Unit


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/login', methods=['get', 'post'])
@loggedin
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            err_msg = 'Username hoặc password không đúng!'

    return render_template('auth/login.html', err_msg=err_msg)


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u and u.role == UserRole.ADMIN:
        login_user(user=u)
    return redirect('/admin')


@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
@loggedin
def register_user():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            avatar_path = None
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            dao.add_user(name=request.form.get('name'),
                         username=request.form.get('username'),
                         password=password,
                         avatar=avatar_path)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('auth/register.html', err_msg=err_msg)


@app.route('/prescription', methods=['GET', 'POST'])
@login_required
@roles_required([UserRole.DOCTOR])
def prescription():
    form = PrescriptionForm()
    categories = dao.get_categorys()
    medicines = dao.get_medicines()
    units = dao.get_units()
    if form.validate_on_submit():
        print("Create Success")
    return render_template('doctor/createprescription.html', form=form, medicines=medicines, cats=categories, units=units)


@app.route('/prescription/create', methods=['POST'])
def create_prescription():
    doctor_id = current_user.id
    date = datetime.today().strftime('%Y-%m-%d')
    patient_id = request.form.get('patient_id')
    symptoms = request.form.get('symptoms')
    diagnosis = request.form.get('diagnosis')
    usages = request.form.getlist('list-usage')
    units = request.form.getlist('list-unit')
    quantities = request.form.getlist('list-quantity')
    medicines = request.form.getlist('list-medicine_id')
    dao.update_list_appointment(patient_id)
    dao.create_medical_form(doctor_id=doctor_id, patient_id=patient_id, date=date, diagnosis=diagnosis,
                            symptoms=symptoms, usages=usages, quantities=quantities, medicines=medicines, units=units)
    # flash("Lập phiếu khám thành công!", 'success')
    print("Create Presciption Successfully!")
    return redirect(url_for('prescription'))


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from clinicapp import admin
        app.run(debug=True)

