import datetime
import hashlib
import hmac
import uuid
import requests
from datetime import date
import cloudinary.uploader
from flask import request, redirect, render_template, jsonify, url_for, current_app, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from clinicapp import app, dao, login, VNPAY_RETURN_URL, VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY, VNPAY_TMN_CODE, \
    TIENKHAM, SOLUONGKHAM, access_key, ipn_url, redirect_url, secret_key, endpoint
from clinicapp.dao import get_quantity_appointment_by_date, get_list_scheduled_hours_by_date_no_confirm, \
    get_list_scheduled_hours_by_date_confirm, get_value_policy
from clinicapp.decorators import loggedin, roles_required
from clinicapp.models import UserRole, Unit
from clinicapp.forms import PrescriptionForm
from clinicapp.vnpay import vnpay


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
    return render_template('doctor/createprescription.html', form=form, medicines=medicines, cats=categories,
                           units=units)


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
            return render_template('/appoinment/patient_create_appoinment.html', appointment_date=appointment_date,
                                   appointment_time=appointment_time, payment_method_id=payment_method_id)
        else:
            appointment_date = datetime.datetime.now().date()
    return render_template('/appoinment/patient_create_appoinment.html', appointment_date=appointment_date)


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


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
