import datetime
import hashlib
import hmac
import json
import locale
import math
import random
import string
import uuid
from random import random as rd

import requests
from PIL import Image
from babel.numbers import format_decimal
from flask import request, redirect, render_template, jsonify, url_for, session, flash
from flask_cors import cross_origin
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import NoResultFound, IntegrityError

from clinicapp import app, dao, login, VNPAY_RETURN_URL, VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY, VNPAY_TMN_CODE, \
    TIENKHAM, SOLUONGKHAM, access_key, ipn_url, redirect_url, secret_key, endpoint, admin, db, utils
from clinicapp.dao import get_quantity_appointment_by_date, get_list_scheduled_hours_by_date_no_confirm, \
    get_prescriptions_by_scheduled_date, get_prescription_by_id, \
    get_medicines_by_prescription_id, get_patient_by_prescription_id, get_medicine_price_by_prescription_id, \
    get_is_paid_by_prescription_id, create_bill, get_bill_by_prescription_id, get_list_scheduled_hours_by_date_confirm, \
    get_value_policy, get_policy_value_by_name, get_unpaid_prescriptions, get_doctor_by_id, \
    get_patient_by_id, get_all_patient, get_all_doctor, get_revenue_percentage_stats
from clinicapp.decorators import loggedin, roles_required, cashiernotloggedin, adminloggedin, resources_owner
from clinicapp.forms import PrescriptionForm, ChangePasswordForm, EditProfileForm, ChangeAvatarForm, ChangeUsernameForm
from clinicapp.models import UserRole, Gender, Appointment, AppointmentList
from clinicapp.vnpay import vnpay
from flask_mail import Mail, Message

mail = Mail(app)


@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')


@app.route('/')
@adminloggedin
def index():  # put application's code here
    return render_template('index.html')


@app.route('/login', methods=['get', 'post'])
def login_my_user():
    err_msg = None
    if current_user.is_authenticated:
        return redirect('/')  # Đã đăng nhập, chuyển hướng đến trang chính
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            next = request.args.get('next')
            if current_user and current_user.role == UserRole.ADMIN:
                return redirect('/admin')
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


@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.json

    if 'username' not in data:
        return jsonify({'error': 'Missing username parameter'}), 400

    username = data['username']

    if dao.get_user_by_username(username) is not None:
        return jsonify({'message': 'Username exists'}), 409
    else:
        return jsonify({'message': 'Username valid'}), 200


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    err_msg = None
    avatar_url = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            avatar = request.files.get('avatar')
            if avatar:
                if avatar.filename != '':
                    img = Image.open(avatar)
                    img_cropped = utils.crop_to_square(img)
                    avatar_url = utils.upload_image_to_cloudinary(img_cropped)
                    if avatar_url:
                        pass
                    else:
                        flash('Đã xảy ra lỗi khi tải lên hình ảnh.', 'danger')
                        avatar_url = "https://www.shutterstock.com/image-vector/default-avatar-profile-icon-social-600nw-1677509740.jpg"
                        return redirect(url_for('register_user'))

            gender = None
            if request.form.get('gender') == 'male':
                gender = Gender.MALE
            else:
                gender = Gender.FEMALE
            try:
                session['patient_cid'] = request.form.get('cid')
                current_user_role = session.pop('current_user_role', None)
                email = request.form.get('email')
                username = request.form.get('username')
                name = request.form.get('name')
                dao.add_user(name=name,
                             username=username,
                             password=password,
                             avatar=avatar_url,
                             email=email,
                             phone=request.form.get('phone'),
                             address=request.form.get('address'),
                             cid=request.form.get('cid'),
                             dob=request.form.get('dob'),
                             gender=gender
                             )
                if current_user_role == 'nurse':
                    send_account_email(email, username, password, name)
                    return redirect('/nurse/nurse_book')
            except IntegrityError as ie:
                if ie.orig.args[0] == 1062:
                    ieMessage = ie.orig.args[1].split()
                    entry = ieMessage[len(ieMessage) - 1]
                    if entry == '\'user.username\'':
                        return redirect(url_for('register_user', err_msg=f'Mã lỗi: 409; Lỗi: Username có rồi!!!'))
                    if entry == '\'user.ix_user_cid\'':
                        return redirect(
                            url_for('register_user', err_msg=f'Mã lỗi: 409; Lỗi: Căng Cước Công Dân này có rồi!!!'))
                    if entry == '\'user.email\'':
                        return redirect(url_for('register_user', err_msg=f'Mã lỗi: 409; Lỗi: Email này có rồi!!!'))

                return redirect(url_for('register_user', err_msg=f'Mã lỗi: {ie.orig.args[0]}; Lỗi: {ie.orig.args[1]}'))
            except Exception as e:
                return redirect(url_for('register_user', err_msg=str(e)))

            return redirect(url_for('login_my_user', success_msg="Tạo tài khoản thành công!!!"))
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('auth/register.html', err_msg=err_msg)


def send_account_email(user_email, user_username, user_password, user_name):
    subject = f'Register account in clinic'
    msg = Message(subject, sender=(app.config['MAIL_SENDER'], app.config['MAIL_SENDER_EMAIL']),
                  recipients=[user_email, '2151013029huy@ou.edu.vn'])
    msg.html = render_template('nurse/account.html', user_username=user_username, user_password=user_password,
                               user_name=user_name)
    mail.send(msg)


@app.route('/list-patient', methods=['GET', 'POST'])
@login_required
@roles_required([UserRole.DOCTOR])
def list_patient():
    return render_template('doctor/list_patient_on_date.html')


@app.route('/api/appointment/approved', methods=['GET'])
@login_required
@roles_required([UserRole.DOCTOR])
def appointment_approved():
    date = request.args.get('date')
    approved_appointments = dao.get_approved_appointments_by_date(date)
    appointments_data = []
    for appointment, user in approved_appointments:
        if user and appointment:
            appointment_data = {
                'patient_id': user.id,
                'name': user.name,
                'cid': user.cid,
                'phone': user.phone,
                'appointment_id': appointment.id,
                'scheduled_date': appointment.scheduled_date.strftime('%d-%m-%Y'),
                'scheduled_hour': str(appointment.scheduled_hour)
            }
            appointments_data.append(appointment_data)
    return jsonify({'appointments': appointments_data})


@app.route('/api/patient/<int:patient_cid>', methods=['POST'])
@cross_origin()
@roles_required([UserRole.DOCTOR])
def get_patient_info(patient_cid):
    scheduled_date = request.json.get('scheduled_date')
    print(scheduled_date)
    patient = dao.get_patient_info(patient_cid=patient_cid, scheduled_date=scheduled_date)
    if patient:
        patient_info = {
            'id': patient[1],
            'name': patient[0],
            'phone': patient[2],
            'email': patient[3],
            'appointment_id': patient[4]
        }
        return jsonify(patient_info)
    else:
        return jsonify({'error': 'Không tìm thấy bệnh nhân'}), 404


@app.route('/prescription', methods=['GET', 'POST'])
@login_required
@roles_required([UserRole.DOCTOR])
def prescription():
    appointment_data = request.form.get('data')
    if appointment_data:
        appointment = json.loads(appointment_data)
    else:
        appointment = None
    form = PrescriptionForm()
    categories = dao.get_categories()
    medicines = dao.get_medicines()
    units = dao.get_units()
    return render_template('doctor/createprescription.html', form=form, appointment=appointment, medicines=medicines,
                           cats=categories,
                           units=units)


@app.route('/prescription/create', methods=['POST'])
@login_required
@roles_required([UserRole.DOCTOR])
def create_prescription():
    doctor_id = current_user.id
    date = datetime.datetime.strptime(request.form.get('date'), '%d-%m-%Y')
    patient_id = request.form.get('patient_id')
    patient_name = request.form.get('name')
    symptoms = request.form.get('symptoms')
    diagnosis = request.form.get('diagnosis')
    appointment_id = request.form.get('appointment_id')
    usages = request.form.getlist('list-usage')
    units = request.form.getlist('list-unit')
    quantities = request.form.getlist('list-quantity')
    medicines = request.form.getlist('list-medicine_id')
    dao.create_prescription(doctor_id=doctor_id, patient_id=patient_id, date=date, diagnosis=diagnosis,
                            symptoms=symptoms, usages=usages, quantities=quantities, medicines=medicines,
                            medicine_units=units, appointment_id=appointment_id)
    flash("Tạo phiếu khám cho bệnh nhân %s thành công!" % patient_name, "success")
    return redirect(url_for('list_patient'))


@app.route('/api/medicines/category/<int:category_id>')
@login_required
def get_medicines_by_category(category_id):
    medicines = dao.get_medicine_by_category(category_id)
    medicines_json = [{'id': medicine.id,
                       'name': medicine.name,
                       'price': medicine.price,
                       'usage': medicine.usage,
                       'exp': medicine.exp
                       } for medicine in medicines]
    return jsonify(medicines_json)


@app.route('/api/medicines/units/<int:medicine_id>')
def get_units_by_medicine(medicine_id):
    units_medicine = dao.get_units_by_medicine(medicine_id)
    units_json = [{'id': unit_medicine.id,
                   'name': dao.get_unit_by_id(unit_medicine.unit_id),
                   } for unit_medicine in units_medicine]
    return jsonify(units_json)


@app.route("/patient/<int:patient_id>/history/")
@login_required
@roles_required([UserRole.DOCTOR, UserRole.PATIENT])
@resources_owner(resource_user_id_param='patient_id', allowed_roles=[UserRole.PATIENT, UserRole.DOCTOR])
def patient_history(patient_id):
    page = request.args.get('page', 1, type=int)
    diagnosis = request.args.get('diagnosis', None, type=str)
    date = request.args.get('start_date', None, type=str)

    patient = dao.get_user_by_id(patient_id)
    prescriptions, count_records = dao.get_prescription_by_patient(patient_id=patient.id, page=page,
                                                                   diagnosis=diagnosis, start_date=date)
    pages = math.ceil(count_records / app.config['PAGE_SIZE'])
    return render_template('doctor/disease_history.html', patient=patient, prescriptions=prescriptions,
                           pages=pages)


@app.route("/api/medicines/")
@login_required
@roles_required([UserRole.DOCTOR])
def get_medicines():
    kw = request.args.get('name')
    medicines = dao.get_medicines(name=kw)
    medicine_list = []
    for medicine in medicines:
        medicine_list.append({
            'id': medicine.id,
            'name': medicine.name,
            'usage': medicine.usage
        })

    return jsonify(medicine_list)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# luc dau tinh lam load form = result nhung fail
@app.route('/patient/book', methods=['GET'])
@roles_required([UserRole.PATIENT])
def book():
    err_msg = None
    if request.method == 'GET':
        appointment_booked = dao.get_appointment_booked_by_patient_id(current_user.id)
        print(appointment_booked)

        if appointment_booked:
            current_patient = current_user
            return render_template('/appointment/patient_create_appoinment.html', appointment_booked=appointment_booked,
                                   current_patient=current_patient)

        date = session.pop('appointment_date', None)
        appointment_time = session.pop('appointment_time', None)
        payment_method_id = session.pop('payment_method_id', None)
        if date is not None and appointment_time is not None:
            appointment_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            return render_template('/appointment/patient_create_appoinment.html', appointment_date=appointment_date,
                                   appointment_time=appointment_time, payment_method_id=payment_method_id,
                                   )
        else:
            appointment_date = datetime.datetime.now().date()
    return render_template('/appointment/patient_create_appoinment.html', appointment_date=appointment_date,
                           current_user_role=current_user.role.value)


def process_vnpay(amount, patient):
    if current_user.role.value == 'patient':
        order_type = "billpayment"
        order_desc = f"Thanh toán viện phí cho bệnh nhân {patient.name}, với số tiền {int(amount)} VND"
        print(patient.name)
        print(patient.id)
        print(amount)
        print(int(dao.get_quantity_history_payment()))
        language = "vn"
        ipaddr = request.remote_addr
        vnp = vnpay()
        vnp.requestData["vnp_Version"] = "2.1.0"
        vnp.requestData["vnp_Command"] = "pay"
        vnp.requestData["vnp_TmnCode"] = VNPAY_TMN_CODE
        vnp.requestData["vnp_Amount"] = int(amount) * 100
        vnp.requestData["vnp_CurrCode"] = "VND"
        vnp.requestData["vnp_TxnRef"] = int(dao.get_quantity_history_payment()) + 1000
        vnp.requestData["vnp_OrderInfo"] = order_desc
        vnp.requestData["vnp_OrderType"] = order_type
        vnp.requestData["vnp_Locale"] = language
        vnp.requestData["vnp_CreateDate"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        vnp.requestData["vnp_IpAddr"] = ipaddr
        vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
        return vnpay_payment_url
    elif current_user.role.value == 'cashier':
        order_type = "billpayment"
        order_desc = f"Thanh toán hoá đơn phiếu khám cho bệnh nhân {patient.name}, với số tiền {int(amount)} VND"
        print(patient.name)
        print(patient.id)
        print(amount)
        print(int(dao.get_quantity_history_payment()))
        language = "vn"
        ipaddr = request.remote_addr
        vnp = vnpay()
        vnp.requestData["vnp_Version"] = "2.1.0"
        vnp.requestData["vnp_Command"] = "pay"
        vnp.requestData["vnp_TmnCode"] = VNPAY_TMN_CODE
        vnp.requestData["vnp_Amount"] = int(amount) * 100
        vnp.requestData["vnp_CurrCode"] = "VND"
        print(patient.id)
        print(1232312312)
        vnp.requestData["vnp_TxnRef"] = int(dao.get_quantity_history_payment()) + 1000
        vnp.requestData["vnp_OrderInfo"] = order_desc
        vnp.requestData["vnp_OrderType"] = order_type
        vnp.requestData["vnp_Locale"] = language
        vnp.requestData["vnp_CreateDate"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        vnp.requestData["vnp_IpAddr"] = ipaddr
        vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
        return vnpay_payment_url


#
# @app.route('/cashier/paybill', methods=['POST'])
# @roles_required([UserRole.CASHIER])
# def cashier_paybill():
#     gateway = request.form.get('way')
#     amount = request.form.get('amount')
#     session['service_price'] = request.form.get('service_price')
#     session['medicine_price'] = request.form.get('medicine_price')
#     session['prescription_id'] = request.form.get('prescription_id')
#     print(gateway)
#     print(amount)
#     print(request.form.get('prescription_id'))
#     print(request.form.get('service_price'))
#     print(request.form.get('medicine_price'))
#     if gateway == 'vnpay':
#         return redirect(process_vnpay(amount, current_user))
#     elif gateway == 'momo':
#         pay = process_momo(amount)
#         print(pay)
#         return redirect(pay)
#     return redirect('/payment')  # Redirect to home page if gateway is invalid


@app.route('/nurse/book_appointment', methods=['POST'])
@roles_required([UserRole.NURSE])
def nurse_book_appointment():
    if current_user.role.value == 'nurse':
        scheduled_date = request.form.get('appointment_date')
        scheduled_minutes = int(request.form.get('appointment_time'))
        scheduled_h = scheduled_minutes // 60
        scheduled_m = scheduled_minutes % 60
        patient_id = session.pop('patient_id', None)

        dao.add_appointment(scheduled_date=scheduled_date,
                            scheduled_hour=datetime.time(scheduled_h, scheduled_m),
                            is_confirm=True,
                            is_paid=False,
                            status=False,
                            patient_id=patient_id)
        flash("Đăng ký lịch hẹn khám thành công!", "success")
        return redirect('/nurse/confirm_appointment')


@app.route('/patient/book_appointment', methods=['POST'])
@roles_required([UserRole.PATIENT])
def patient_book_appointment():
    if current_user.role.value == 'patient':
        pay_method = request.form.get('payment_method')
        gateway = request.form.get('way')
        if pay_method == 'direct':
            session['appointment_date'] = request.form.get('appointment_date')
            session['appointment_time'] = request.form.get('appointment_time')
            session['payment_method'] = pay_method
            session['way'] = gateway
            amount = get_value_policy(TIENKHAM)
            if gateway == 'vnpay':
                return redirect(process_vnpay(amount, current_user))
            elif gateway == 'momo':
                return redirect(process_momo(amount))

        elif pay_method == 'clinic':
            scheduled_date = request.form.get('appointment_date')
            scheduled_minutes = int(request.form.get('appointment_time'))
            scheduled_h = scheduled_minutes // 60
            scheduled_m = scheduled_minutes % 60
            print(scheduled_h)
            print(scheduled_m)
            print(current_user.id)

            dao.add_appointment(scheduled_date=scheduled_date,
                                scheduled_hour=datetime.time(scheduled_h, scheduled_m),
                                is_confirm=False,
                                is_paid=False,
                                status=False,
                                patient_id=current_user.id)
            flash("Đăng ký lịch hẹn khám thành công!", "success")

            return redirect('/patient/book')


def create_appoinment_done_payment():
    appointment_date = session.pop('appointment_date', None)
    appointment_time = int(session.pop('appointment_time', None))
    scheduled_h = appointment_time // 60
    scheduled_m = appointment_time % 60
    dao.add_appointment(scheduled_date=appointment_date,
                        scheduled_hour=datetime.time(scheduled_h, scheduled_m),
                        is_confirm=True,
                        is_paid=True,
                        status=False,
                        patient_id=current_user.id)


@app.route('/payment_return_vnpay', methods=['GET'])
def payment_return():
    inputData = request.args
    vnp = vnpay()
    vnp.responseData = inputData.to_dict()
    vnp_ResponseCode = inputData["vnp_ResponseCode"]
    vnp_Amount = int(inputData["vnp_Amount"])
    trans_code = inputData["vnp_BankTranNo"]
    print(inputData)
    print(155555)
    # Kiểm tra tính toàn vẹn của dữ liệu
    if vnp_ResponseCode == "00":
        # Lấy thông tin lịch hẹn từ request và thông tin người dùng hiện tại
        if current_user.role.value == 'patient':
            create_appoinment_done_payment()
            dao.create_order_payment(amount=vnp_Amount, gateway='vnpay', patient_id=current_user.id, paid=True,
                                     response_code=trans_code)
            flash("Đăng ký lịch hẹn khám thành công!", "success")
            return redirect('/patient/book')
        elif current_user.role.value == 'cashier':
            print(43434)
            dao.create_order_payment(amount=vnp_Amount, gateway='vnpay',
                                     patient_id=session.pop('current_patient_id', None), paid=True,
                                     response_code=trans_code)
            error = None
            created = True

            prescription_id = session.pop('prescription_id', None)
            service_price = session.pop('service_price', None)
            medicine_price = session.pop('medicine_price', None)
            create_bill(
                service_price=service_price,
                medicine_price=medicine_price,
                total=vnp_Amount,
                cashier_id=current_user.id,
                prescription_id=prescription_id
            )
            return redirect(url_for('do_bill',
                                    prescription_id=prescription_id,
                                    error=error,
                                    created=created
                                    ))

    else:
        # Xử lý trường hợp lỗi từ VNPAY
        return redirect('/')


@app.route('/payment_return_momo', methods=['GET'])
def payment_return_momo():
    inputData = request.args
    resultCode = str(inputData["resultCode"])
    print(resultCode)
    # Kiểm tra tính toàn vẹn của dữ liệu
    if resultCode == "0":
        # Lấy thông tin lịch hẹn từ request và thông tin người dùng hiện tại
        if current_user.role.value == 'patient':
            create_appoinment_done_payment()
            amount = inputData["amount"]
            trans_code = inputData["transId"]
            print(trans_code)
            dao.create_order_payment(amount=amount, gateway='momo', patient_id=current_user.id, paid=True,
                                     response_code=trans_code)

            # create_appoinment_done_payment()
            flash("Đăng ký lịch hẹn khám thành công!", "success")
            return redirect('/patient/book')
        elif current_user.role.value == 'cashier':
            amount = inputData["amount"]
            trans_code = inputData["transId"]
            print(trans_code)
            patient_id = session.pop("current_patient_id", None)
            dao.create_order_payment(amount=amount, gateway='momo', patient_id=patient_id, paid=True,
                                     response_code=trans_code)
            prescription_id = session.pop('prescription_id', None)
            service_price = session.pop('service_price', None)
            medicine_price = session.pop('medicine_price', None)
            create_bill(
                service_price=service_price,
                medicine_price=medicine_price,
                total=amount,
                cashier_id=current_user.id,
                prescription_id=prescription_id
            )
            return redirect('/payment')
    else:
        return redirect('/')


@app.route('/check-appointment-date', methods=['GET'])
def check_appointment_date():
    date = request.args.get('date')  # Lấy ngày từ yêu cầu GET
    today = datetime.datetime.now().date().isoformat()

    if not date or date < today:
        return jsonify({'status': 'invalid_date'})
    quantity = get_quantity_appointment_by_date(date)
    # print(quantity)
    policy = int(get_value_policy(SOLUONGKHAM))
    print(policy)
    print(11111)
    print(quantity)
    # print(policy)
    if quantity < policy:
        return jsonify({'status': 'available'})
    else:
        return jsonify({'status': 'unavailable'})


@app.route('/get-scheduled-hour-no-confirm', methods=['GET'])
def get_scheduled_hour_no_confirm():
    date = request.args.get('date')  # Lấy ngày từ yêu cầu GET
    list_unavailable_hour = get_list_scheduled_hours_by_date_no_confirm(date)
    formatted_hours = [hour.strftime('%H:%M') for hour in list_unavailable_hour]
    print(formatted_hours)
    return jsonify(formatted_hours)


@app.route('/get-scheduled-hour-confirm', methods=['GET'])
def get_scheduled_hour_confirm():
    date = request.args.get('date')  # Lấy ngày từ yêu cầu GET
    list_unavailable_hour = get_list_scheduled_hours_by_date_confirm(date)
    formatted_hours = [hour.strftime('%H:%M') for hour in list_unavailable_hour]
    print(formatted_hours)
    return jsonify(formatted_hours)


def process_momo(amount):
    if current_user.role.value == 'patient':
        order_info = "Thanh toan phi kham benh"
    elif current_user.role.value == 'cashier':
        order_info = "Thanh toan hoa don phieu kham benh"
    # Tạo orderId và requestId
    order_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    # Tạo chuỗi chữ ký
    raw_signature = "accessKey=" + access_key + "&amount=" + str(amount) + "&extraData=" + "" \
                    + "&ipnUrl=" + ipn_url + "&orderId=" + order_id + "&orderInfo=" + order_info \
                    + "&partnerCode=MOMO" + "&redirectUrl=" + redirect_url + "&requestId=" + request_id \
                    + "&requestType=captureWallet"
    h = hmac.new(bytes(secret_key, 'ascii'), bytes(raw_signature, 'ascii'), hashlib.sha256)
    signature = h.hexdigest()

    # Tạo dữ liệu gửi đến MoMo
    data = {
        'partnerCode': 'MOMO',
        'partnerName': 'Test',
        'storeId': 'MomoTestStore',
        'requestId': request_id,
        'amount': str(amount),
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': redirect_url,
        'ipnUrl': ipn_url,
        'lang': 'vi',
        'extraData': '',
        'requestType': 'captureWallet',
        'signature': signature
    }
    # Gửi yêu cầu thanh toán đến MoMo
    response = requests.post(endpoint, json=data)
    # Xử lý kết quả trả về từ MoMo
    if response.status_code == 200:
        response_data = response.json()
        if 'payUrl' in response_data:
            # Nếu thành công, trả về URL thanh toán cho frontend
            payUrl = response_data['payUrl']
            print(payUrl)
            return payUrl
        else:
            return jsonify({'error': 'Failed to process payment'}), 500
    else:
        return jsonify({'error': 'Failed to communicate with MoMo'}), 500


@app.route('/payment', methods=['GET'])
@cashiernotloggedin
def pay():
    q = request.args.get('q') or session.get('date')
    prescriptions = get_unpaid_prescriptions(scheduled_date=q)

    session['date'] = q

    return render_template('cashier/payment.html',
                           prescriptions=prescriptions,
                           date=session['date'] if session.get('date') else None,
                           allpatients=get_all_patient(),
                           alldoctors=get_all_doctor(),
                           )


@app.route('/payment/all', methods=['GET'])
@cashiernotloggedin
def pay_all():
    prescriptions = get_unpaid_prescriptions(scheduled_date=None)

    return render_template('cashier/payment.html',
                           prescriptions=prescriptions,
                           date=session['date'] if session.get('date') else None,
                           allpatients=get_all_patient(),
                           alldoctors=get_all_doctor(),
                           )


@app.route('/api/get-doctor/<doctor_id>', methods=['POST'])
def get_doctor(doctor_id):
    return get_doctor_by_id(doctor_id)


@app.route('/api/get-patient/<patient_id>', methods=['POST'])
def get_patient(patient_id):
    return get_patient_by_id(patient_id)


@app.route('/bills/<prescription_id>', methods=['GET', 'POST'])
@cashiernotloggedin
def do_bill(prescription_id):
    try:
        global error, created
        current_prescription = get_prescription_by_id(prescription_id)
        current_patient = get_patient_by_prescription_id(prescription_id)
        session['current_patient_id'] = current_patient.id
        session['prescription_id'] = prescription_id
        current_medicines = get_medicines_by_prescription_id(prescription_id)
        medicine_price = get_medicine_price_by_prescription_id(prescription_id)

        service_price = get_policy_value_by_name('tien_kham')
        if not service_price:
            service_price = 0
        total = medicine_price
        is_paid = get_is_paid_by_prescription_id(prescription_id)
        print(is_paid)
        if not is_paid:
            total += service_price

        if request.method.__eq__('POST'):
            get_payment = request.form.get('optradio')
            gateway = request.form.get('way')
            amount = total
            session['service_price'] = request.form.get('service_price')
            session['medicine_price'] = request.form.get('medicine_price')

            if get_payment == 'radio_offline':
                try:
                    if len(get_bill_by_prescription_id(prescription_id)) > 0:
                        raise Exception("Bill này có rồi!!!")

                    create_bill(
                        service_price=service_price,
                        medicine_price=medicine_price,
                        total=total,
                        cashier_id=current_user.id,
                        prescription_id=prescription_id
                    )

                    error = None
                    created = True
                except Exception as e:
                    error = str(e)
                    created = False
                finally:
                    return redirect(url_for('do_bill',
                                            prescription_id=prescription_id,
                                            error=error,
                                            created=created
                                            ))
            elif get_payment == 'radio_online':
                if gateway == 'vnpay':
                    return redirect(process_vnpay(amount, current_patient))
                elif gateway == 'momo':
                    print(amount)
                    print(32423423)
                    pay = process_momo(int(amount))
                    print(pay)
                    return redirect(pay)
                return redirect('/payment')
            elif get_payment == 'none':
                error = "none"
                created = False
                return redirect(url_for('do_bill',
                                        prescription_id=prescription_id,
                                        error=error,
                                        created=created
                                        ))
        q_error = request.args.get('error')
        q_created = request.args.get('created')
        print(format_decimal(medicine_price, locale='de_DE'))
        return render_template('cashier/bill.html',
                               prescription=current_prescription,
                               medicines=current_medicines,
                               patient=current_patient,
                               medicine_price=medicine_price,
                               service_price=service_price,
                               is_paid=is_paid,
                               total=total,
                               error=q_error,
                               created=q_created
                               )
    except Exception as e:
        print(str(e))


@app.route('/profile')
@login_required
def profile():
    form = ChangeAvatarForm()
    return render_template('profile/profile.html', change_avatar_form=form)


@app.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.cid = form.cid.data
        current_user.dob = form.dob.data
        current_user.phone = form.phone.data
        current_user.email = form.email.data
        current_user.gender = form.gender.data
        current_user.address = form.address.data
        db.session.commit()
        flash("Cập nhật thông tin người dùng thành công!", "success")
        return redirect(url_for('profile'))
    form.name.data = current_user.name
    form.cid.data = current_user.cid
    form.dob.data = current_user.dob
    form.phone.data = current_user.phone
    form.email.data = current_user.email
    form.gender.data = current_user.gender
    form.address.data = current_user.address
    return render_template('profile/edit_profile.html', form=form)


@app.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def profile_change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_pass = form.old_password.data.strip()
        new_pass = form.new_password.data.strip()
        if dao.verify_password(old_pass, current_user.password):
            current_user.password = dao.hash_password(new_pass)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('profile'))
        flash('Mật khẩu không đúng!', 'danger')
    return render_template('profile/change_password.html', form=form)


@app.route('/profile/change_username', methods=['GET', 'POST'])
@login_required
def profile_change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        current_user.username = form.new_username.data.strip()
        db.session.commit()
        flash('Đổi tên tài khoản thành công!', 'success')
        return redirect(url_for('profile'))

    form.old_username.data = current_user.username
    return render_template('profile/change_username.html', form=form)


@app.route('/profile/change_avatar', methods=['POST'])
def profile_change_avatar():
    form = ChangeAvatarForm()
    if form.validate_on_submit():
        if 'avatar' in request.files:
            file_to_upload = request.files['avatar']
            if file_to_upload.filename != '':
                img = Image.open(file_to_upload)
                img_cropped = utils.crop_to_square(img)

                # Upload hình ảnh đã cắt lên Cloudinary
                new_avatar_url = utils.upload_image_to_cloudinary(img_cropped)
                if new_avatar_url:
                    current_user.avatar = new_avatar_url
                    db.session.commit()
                    flash('Đã đổi avatar thành công.', 'success')
                    return redirect(url_for('profile'))
                else:
                    flash('Đã xảy ra lỗi khi tải lên hình ảnh.', 'danger')
            else:
                flash('Vui lòng chọn hình ảnh để tải lên.', 'danger')
        else:
            flash('Không có hình ảnh được gửi.', 'danger')
    else:
        flash('Form không hợp lệ.', 'danger')
    return redirect(url_for('profile'))


@app.route('/nurse/approved_appointment', methods=['GET'])
@login_required
@roles_required([UserRole.NURSE])
def approved_appointment():
    date = request.args.get('approved-date')  # Lấy ngày từ
    print(date)
    approved_appointments = dao.get_approved_appointments_by_date(date)
    print(approved_appointments)
    return render_template("/appointment/approved_appointments.html", approved_appointments=approved_appointments)


@roles_required([UserRole.NURSE])
@login_required
@app.route('/nurse/confirm_appointment', methods=['GET'])
def confirm_appointment():
    date = request.args.get('date')  # Lấy ngày từ yêu cầu GET
    get_list_appointment_no_confirm = dao.get_list_appointment_no_confirm_by_date(date)
    print(get_list_appointment_no_confirm)
    get_list_appointment_confirm = dao.get_list_appointment_confirm_by_date(date)

    return render_template('nurse/confirm_appointment.html', appointments_no_confirm=get_list_appointment_no_confirm,
                           appointments_confirm=get_list_appointment_confirm)


@app.route('/nurse/change_confirm', methods=['POST'])
def change_confirm():
    data = request.json
    appointment_id = data.get('id')
    scheduled_date = data.get('scheduled_date')
    scheduled_hour = data.get('scheduled_hour')

    if appointment_id is None or scheduled_date is None or scheduled_hour is None:
        return 'Invalid request. Missing required parameters.', 400

    flag = dao.conflict_appointment(scheduled_date, scheduled_hour)
    if flag:
        return 'There is a conflicting appointment. Please choose another date and time.', 400
    else:
        dao.update_confirm_appointment(appointment_id)
        print(appointment_id)
        return 'Success', 200


@app.route('/api/update_appointment', methods=['PATCH'])
def update_appointment():
    new_status = request.args.get('status')
    if current_user.role.value == 'nurse':
        if new_status in ['approved', 'cancelled']:
            if new_status == 'cancelled':
                appointment_id = request.args.get('appointment_id')
                user_id = request.args.get('user_id')
                new_user = dao.get_user_by_id(user_id)
                new_appointment = dao.get_appointment_by_id(appointment_id)
                if new_appointment is None:
                    return jsonify({'error': 'Appointment not found.'}), 404
                send_notification_email(new_user, new_appointment, "TỪ CHỐI")
                dao.delete_appointment(new_appointment)
                return jsonify({'message': 'Appointment status updated successfully.'}), 200
            elif new_status == 'approved':
                card_data = request.json
                # for card in card_data:
                #     appointment_id = card.get('appointment_id')
                #     appointment = Appointment.query.get(appointment_id)
                #     if appointment:
                #         appointment.status = True  # Đổi status thành True
                #         appointment_list = AppointmentList.query.filter_by(scheduled_date=appointment.scheduled_date).first()
                #         if appointment_list:
                #             appointment.appointment_list_id = appointment_list.id  # Gắn AppointmentList_id
                #         db.session.commit()ard
                dao.make_the_list(card_data)
                return jsonify({'message': 'Card data processed successfully'}), 200
    elif current_user.role.value == 'patient':
        print(123123123123123123)
        if new_status == 'cancelled':
            appointment_id = request.args.get('appointment_id')
            new_appointment = dao.get_appointment_by_id(appointment_id)
            if new_appointment is None:
                return jsonify({'error': 'Appointment not found.'}), 404
            send_notification_email(current_user, new_appointment, "ĐƯỢC HUỶ")
            dao.delete_appointment(new_appointment)
            flash("Huỷ lịch hẹn khám thành công!", "success")
            return jsonify({'message': 'Card data processed successfully'}), 200
        elif new_status == 'approved':
            pass
    return jsonify({'error': 'Invalid status value.'}), 400


@app.route('/nurse/send_list_email', methods=['POST'])
def send_list_email():
    data = request.json
    for entry in data:
        appointment_id = entry.get('appointment_id')
        user_id = entry.get('user_id')
        new_user = dao.get_user_by_id(user_id)
        new_appointment = dao.get_appointment_by_id(appointment_id)
        print(new_user)
        print(new_appointment)
        print(1222)
        send_notification_email(new_user, new_appointment, "ĐƯỢC DUYỆT")
        print(1222)

    return jsonify({'message': 'Email notifications sent successfully.'}), 200


def send_notification_email(user, appointment, status):
    # appointment.status = True  # Assuming True represents cancelled status in your database
    subject = f'Appointment Status Changed DateTime: {appointment.scheduled_date} - {appointment.scheduled_hour}'
    # body = f"Dear {new_user.name}, \nYour appointment status has been {
    # new_status} " \ #        f"from to " \ #        f"\nRegards,\nThe Private Clinic Team"
    data = {
        'user': user,
        'appointment': appointment,
        'status': "HUỶ"
    }
    print(data)
    # Gửi email
    msg = Message(subject, sender=(app.config["MAIL_SENDER"], app.config["MAIL_SENDER_EMAIL"]),
                  recipients=[user.email, '2151013029huy@ou.edu.vn'])
    # msg.body = body
    msg.html = render_template('nurse/email.html', user=user, appointment=appointment, status=status)
    mail.send(msg)


# @app.route('/test')
# def test_mail():  # Renamed the function to avoid naming conflict
#     msg = Message('ssdasdasd', sender='peteralwaysloveu@gmail.com',
#                   recipients=['baoempro2003@gmail.com', '2151013029huy@ou.dedu.vn', ])
#     msg.body = "clinic asdasdasdasd"
#     mail.send(msg)
#     return "success"


@app.route('/nurse/create_list_by_date', methods=['POST'])
def create_list_by_date():
    data = request.json
    scheduled_dates = data.get('scheduled_dates', [])
    scheduled_dates = [datetime.datetime.strptime(date_str.split(": ")[1], "%Y-%m-%d").date() for date_str in
                       scheduled_dates]

    # for scheduled_date in scheduled_dates:
    #     if not AppointmentList.query.filter_by(scheduled_date=scheduled_date).first():
    #         new_appointment_list = AppointmentList(scheduled_date=scheduled_date)
    #         db.session.add(new_appointment_list)
    #         db.session.commit()
    date_range = dao.get_date_range()
    print(scheduled_dates)
    print(dao.get_date_range())
    unique_dates = list(filter(lambda date: date not in date_range, scheduled_dates))
    print(222)
    print(unique_dates)
    try:
        # Tạo mới các AppointmentList cho các ngày không trùng
        for scheduled_date in unique_dates:
            new_appointment_list = AppointmentList(scheduled_date=scheduled_date, nurse_id=current_user.id)
            db.session.add(new_appointment_list)
        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()
        return jsonify({'message': 'Appointment lists created successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Failed to create appointment lists'}), 500


# @app.route('/nurse/process_card_data', methods=['POST'])
# def process_card_data():
#
#     card_data = request.json
#     dao.make_the_list(card_data)
#     return jsonify({'message': 'Card data processed successfully'}), 200

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@app.route('/nurse/nurse_book', methods=['GET'])
def nure_book():
    patient_cid = None
    patient_cid = request.args.get('patient_cid')
    session['current_user_role'] = current_user.role.value

    if patient_cid is None:
        patient_cid = session.pop('patient_cid', None)
    current_patient = None
    if patient_cid:
        current_patient = dao.get_patient_by_cid(patient_cid)
        print(current_patient)
        if current_patient:
            appointment_booked = dao.get_appointment_booked_by_patient_id(current_patient.id)
            appointment_date = datetime.datetime.now().date()
            current_user_role = current_user.role.value
            session['patient_id'] = current_patient.id
            return render_template('/appointment/nurse_create_appointment.html', current_patient=current_patient,
                                   patient_cid=patient_cid, appointment_booked=appointment_booked,
                                   appointment_date=appointment_date, current_user_role=current_user_role)
        else:
            flash("Không có người dùng trong hệ thống!", "success")
    return render_template('/appointment/nurse_create_appointment.html', current_patient=current_patient,
                           patient_cid=patient_cid)


@app.route('/api/revenue_percentage_stats/', methods=['POST'])
def revenue_percentage_stats():
    month_str = request.json.get('month')
    print(month_str)
    if month_str:
        stats_list = get_revenue_percentage_stats(month_str=month_str)
        return stats_list


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = dao.get_user_by_username(username)
        characters = string.ascii_letters + string.punctuation
        random_password = ''.join(random.choice(characters) for _ in range(9))
        user.password = dao.hash_password(random_password)
        send_account_email(user_email=user.email, user_username=username, user_password=random_password,
                           user_name=user.name)
        db.session.commit()
        # flash('Chúng tôi đã gửi hướng dẫn khôi phục mật khẩu cho bạn. Vui lòng kiểm tra email của bạn.', 'success')
        return redirect('/login')
    return render_template('/auth/forgot_password.html')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
