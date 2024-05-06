import datetime
import hashlib
import hmac
import uuid
import requests
from datetime import date
import cloudinary.uploader
from flask import request, redirect, render_template, jsonify, url_for, current_app, flash, session
from flask_cors import cross_origin
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound

from clinicapp import app, dao, login, VNPAY_RETURN_URL, VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY, VNPAY_TMN_CODE, \
    TIENKHAM, SOLUONGKHAM, access_key, ipn_url, redirect_url, secret_key, endpoint
from clinicapp.dao import *
from clinicapp.decorators import loggedin, roles_required, cashiernotloggedin
from clinicapp.models import UserRole, Unit
from clinicapp.forms import PrescriptionForm
from clinicapp.vnpay import vnpay
from flask_mail import Mail, Message

mail = Mail(app)


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


@app.route('/api/patient/<int:patient_cid>', methods=['GET'])
@cross_origin()
def get_patient_info(patient_cid):
    patient = dao.get_patient_info(patient_cid=patient_cid)
    if patient:
        patient_info = {
            'id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'email': patient.email,
        }
        return jsonify(patient_info)
    else:
        return jsonify({'error': 'Không tìm thấy bệnh nhân'}), 404


@app.route('/prescription', methods=['GET', 'POST'])
@login_required
@roles_required([UserRole.DOCTOR])
def prescription():
    form = PrescriptionForm()
    categories = dao.get_categories()
    medicines = dao.get_medicines()
    units = dao.get_units()
    if form.validate_on_submit():
        print("Create Success")
    return render_template('doctor/createprescription.html', form=form, medicines=medicines, cats=categories,
                           units=units)


@app.route('/prescription/create', methods=['POST'])
def create_prescription():
    doctor_id = current_user.id
    date = datetime.date.today().strftime('%Y-%m-%d')
    patient_id = request.form.get('patient_id')
    symptoms = request.form.get('symptoms')
    diagnosis = request.form.get('diagnosis')
    usages = request.form.getlist('list-usage')
    units = request.form.getlist('list-unit')
    quantities = request.form.getlist('list-quantity')
    medicines = request.form.getlist('list-medicine_id')
    dao.update_list_appointment(patient_id)
    dao.create_prescription(doctor_id=doctor_id, patient_id=patient_id, date=date, diagnosis=diagnosis,
                            symptoms=symptoms, usages=usages, quantities=quantities, medicines=medicines, units=units)
    # flash("Lập phiếu khám thành công!", 'success')
    print("Create Presciption Successfully!")
    return redirect(url_for('prescription'))


@app.route('/api/medicines/category/<int:category_id>')
def get_medicines_by_category(category_id):
    medicines = dao.get_medicine_by_category(category_id)
    medicines_json = [{'id': medicine.id,
                       'name': medicine.name,
                       'price': medicine.price,
                       'usage': medicine.usage,
                       'exp': medicine.exp
                       } for medicine in medicines]
    return jsonify(medicines_json)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# luc dau tinh lam load form = result nhung fail
@app.route('/patient/book', methods=['GET'])
def book():
    err_msg = None
    if request.method == 'GET':
        date = session.pop('appointment_date', None)
        appointment_time = session.pop('appointment_time', None)
        payment_method_id = session.pop('payment_method_id', None)
        print(current_user.role.value)
        print(date)
        print(appointment_time)
        print(payment_method_id)

        if date is not None and appointment_time is not None:
            appointment_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            return render_template('/appointment/patient_create_appoinment.html', appointment_date=appointment_date,
                                   appointment_time=appointment_time, payment_method_id=payment_method_id)
        else:
            appointment_date = datetime.datetime.now().date()
    return render_template('/appointment/patient_create_appoinment.html', appointment_date=appointment_date)


def process_vnpay(amount, patient):
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
    vnp.requestData["vnp_TxnRef"] = patient.id + int(dao.get_quantity_history_payment())
    vnp.requestData["vnp_OrderInfo"] = order_desc
    vnp.requestData["vnp_OrderType"] = order_type
    vnp.requestData["vnp_Locale"] = language
    vnp.requestData["vnp_CreateDate"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vnp.requestData["vnp_IpAddr"] = ipaddr
    vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
    return vnpay_payment_url


@app.route('/patient/book-appointment', methods=['POST'])
def patient_book_appointment():
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
        return redirect('/')


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

    # Kiểm tra tính toàn vẹn của dữ liệu
    if vnp_ResponseCode == "00":
        # Lấy thông tin lịch hẹn từ request và thông tin người dùng hiện tại
        if current_user.role.value == 'patient':
            create_appoinment_done_payment()
            amount = get_value_policy(TIENKHAM)
            trans_code = inputData["vnp_BankTranNo"]
            dao.create_order_payment(amount=amount, gateway='vnpay', patient_id=current_user.id, paid=True,
                                     response_code=trans_code)
            return redirect('/')
        elif current_user.role.value == 'nurse':
            pass
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
            amount = get_value_policy(TIENKHAM)
            trans_code = inputData["transId"]
            print(trans_code)
            dao.create_order_payment(amount=amount, gateway='momo', patient_id=current_user.id, paid=True,
                                     response_code=trans_code)
            # create_appoinment_done_payment()
            return redirect('/')
        elif current_user.role.value == 'nurse':
            pass
    else:
        # Xử lý trường hợp lỗi từ VNPAY
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
    elif current_user.role.value == 'nurse':
        order_info = "Thanh toan hoa don kham benh"
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
    prescriptions = None
    if q:
        prescriptions = get_prescriptions_by_scheduled_date(date=q)
        session['date'] = q

    return render_template('cashier/payment.html',
                           prescriptions=prescriptions,
                           date=session['date'] if session.get('date') else None
                           )


@app.route('/bills/<prescription_id>', methods=['GET', 'POST'])
@cashiernotloggedin
def do_bill(prescription_id):
    global error, created
    current_prescription = get_prescription_by_id(prescription_id)
    current_patient = get_patient_by_prescription_id(prescription_id)
    current_medicines = get_medicines_by_prescription_id(prescription_id)
    medicine_price = get_medicine_price_by_prescription_id(prescription_id)

    # cai nay khi nao thong nhat policy xong thi replace value khac
    service_price = 100000
    total = medicine_price
    is_paid = get_is_paid_by_prescription_id(prescription_id)

    if not is_paid:
        total += service_price

    if request.method.__eq__('POST'):
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

    q_error = request.args.get('error')
    q_created = request.args.get('created')

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


@app.route('/nurse/confirm_appointment', methods=['GET'])
def confirm_appointment():
    date = request.args.get('date')  # Lấy ngày từ yêu cầu GET
    get_list_appointment_no_confirm = dao.get_list_appointment_no_confirm_by_date(date)
    print(get_list_appointment_no_confirm)
    get_list_appointment_confirm = dao.get_list_appointment_confirm_by_date(date)

    return render_template('nurse/confirm_appointment.html', appointments_no_confirm=get_list_appointment_no_confirm,
                           appointments_confirm=get_list_appointment_confirm)


@app.route('/nurse/approved_appointment', methods=['GET'])
def approved_appointment():
    date = request.args.get('approved-date')  # Lấy ngày từ
    print(date)
    approved_appointments = dao.get_approved_appointments_by_date(date)
    print(approved_appointments)
    return render_template("/appointment/approved_appointments.html", approved_appointments=approved_appointments )


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


@app.route('/nurse/status-change', methods=['PATCH'])
def status_change():
    appointment_id = request.args.get('appointment_id')
    user_id = request.args.get('user_id')
    new_user = dao.get_user_by_id(user_id)
    new_appointment = dao.get_appointment_by_id(appointment_id)
    new_status = request.args.get('status')

    if new_appointment is None:
        return jsonify({'error': 'Appointment not found.'}), 404

    if new_status in ['approved', 'cancelled']:
        if new_status == 'cancelled':
            print(2222)
        # new_appointment.status = True  # Assuming True represents cancelled status in your database
        # # subject = f'Appointment Status Changed DateTime: #{new_appointment.scheduled_date} - {
        # # new_appointment.scheduled_hour}' # body = f"Dear {new_user.name}, \nYour appointment status has been {
        # # new_status} " \ #        f"from to " \ #        f"\nRegards,\nThe Private Clinic Team"
        # data = {
        #     'user': new_user,
        #     'appointment': new_appointment,
        #     'status': "HUỶ"
        # }
        # print(data)
        # # Gửi email
        # msg = Message('qweqwe', sender='peteralwaysloveu@gmail.com',
        #               recipients=[new_user.email, '2151010419tuan@ou.edu.vn'])
        # # msg.body = body
        # msg.html = render_template('nurse/email.html', user=new_user, appointment=new_appointment, status="HUỶ")
        # mail.send(msg)
        # dao.delete_appointment(new_appointment)
        send_notification_email(new_user, new_appointment, "TỪ CHỐI")
        return jsonify({'message': 'Appointment status updated successfully.'}), 200
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
    msg = Message(subject, sender='peteralwaysloveu@gmail.com',
                  recipients=[user.email, '2151013029huy@ou.edu.vn'])
    # msg.body = body
    msg.html = render_template('nurse/email.html', user=user, appointment=appointment, status=status)
    mail.send(msg)
    dao.delete_appointment(appointment)
    return jsonify({'message': 'Appointment status updated successfully.'}), 200


@app.route('/test')
def test_mail():  # Renamed the function to avoid naming conflict
    msg = Message('ssdasdasd', sender='peteralwaysloveu@gmail.com',
                  recipients=['baoempro2003@gmail.com', '2151013029huy@ou.dedu.vn', ])
    msg.body = "clinic asdasdasdasd"
    mail.send(msg)
    return "success"


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


@app.route('/nurse/process_card_data', methods=['POST'])
def process_card_data():
    # for card in card_data:
    #     appointment_id = card.get('appointment_id')
    #     appointment = Appointment.query.get(appointment_id)
    #     if appointment:
    #         appointment.status = True  # Đổi status thành True
    #         appointment_list = AppointmentList.query.filter_by(scheduled_date=appointment.scheduled_date).first()
    #         if appointment_list:
    #             appointment.appointment_list_id = appointment_list.id  # Gắn AppointmentList_id
    #         db.session.commit()
    card_data = request.json
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
    return jsonify({'message': 'Card data processed successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
