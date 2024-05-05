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

from clinicapp import app, dao, login, VNPAY_RETURN_URL, VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY, VNPAY_TMN_CODE, \
    TIENKHAM, SOLUONGKHAM
from clinicapp.dao import get_quantity_appointment_by_date, get_list_scheduled_hours_by_date_no_confirm, \
    get_list_scheduled_hours_by_date_confirm, get_prescriptions_by_scheduled_date, get_prescription_by_id, \
    get_medicines_by_prescription_id, get_patient_by_prescription_id, get_medicine_price_by_prescription_id, \
    get_is_paid_by_prescription_id, create_bill, get_bill_by_prescription_id, get_list_scheduled_hours_by_date_confirm, get_value_policy
from clinicapp.decorators import loggedin, roles_required, cashiernotloggedin
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
    if request.method.__eq__('POST'):
        date = request.args.get('date')
        current_user.id
        return 0
    return render_template('/appoinment/patient_create_appoinment.html')


@app.route('/patient/book-appointment', methods=['POST'])
def patient_book_appointment():
    pay_method = request.form.get('payment_method')

    if pay_method == 'direct':
        session['appointment_date'] = request.form.get('appointment_date')
        session['appointment_time'] = request.form.get('appointment_time')
        order_type = "billpayment"
        amount = int(get_value_policy(TIENKHAM))
        order_desc = f"Thanh toán viện phí cho bệnh nhân {current_user.name}, với số tiền {amount} VND"
        language = "vn"
        ipaddr = request.remote_addr

        vnp = vnpay()
        vnp.requestData["vnp_Version"] = "2.1.0"
        vnp.requestData["vnp_Command"] = "pay"
        vnp.requestData["vnp_TmnCode"] = VNPAY_TMN_CODE
        vnp.requestData["vnp_Amount"] = amount * 100
        vnp.requestData["vnp_CurrCode"] = "VND"
        vnp.requestData["vnp_TxnRef"] = current_user.id + 1010131111211111
        vnp.requestData["vnp_OrderInfo"] = order_desc
        vnp.requestData["vnp_OrderType"] = order_type
        vnp.requestData["vnp_Locale"] = language
        vnp.requestData["vnp_CreateDate"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        vnp.requestData["vnp_IpAddr"] = ipaddr
        vnp.requestData["vnp_ReturnUrl"] = VNPAY_RETURN_URL

        vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
        return redirect(vnpay_payment_url)
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

@app.route('/payment-return', methods=['GET'])
def payment_return():
    inputData = request.args
    vnp = vnpay()
    vnp.responseData = inputData.to_dict()
    vnp_ResponseCode = inputData["vnp_ResponseCode"]

    # Kiểm tra tính toàn vẹn của dữ liệu
    if vnp_ResponseCode == "00":
        # Lấy thông tin lịch hẹn từ request và thông tin người dùng hiện tại

        appointment_date = session.pop('appointment_date', None)
        appointment_time = int(session.pop('appointment_time', None))
        scheduled_h = appointment_time // 60
        scheduled_m = appointment_time % 60
        # Lưu thông tin lịch hẹn vào cơ sở dữ liệu
        dao.add_appointment(scheduled_date=appointment_date,
                            scheduled_hour=datetime.time(scheduled_h, scheduled_m),
                            is_confirm=True,
                            is_paid=True,
                            status=False,
                            patient_id=current_user.id)
        # Hiển thị thông báo thành công và chuyển hướng về trang đặt lịch hẹn
        flash("Thanh toán hóa đơn thành công. Lịch hẹn của bạn đã được tạo.", category="success")
        return redirect('/')
    else:
        # Xử lý trường hợp lỗi từ VNPAY
        flash("Có lỗi xảy ra từ VNPAY. Mã lỗi: {}".format(vnp_ResponseCode), category="danger")
        return redirect('/')


@app.route('/process-payment', methods=['POST'])
def process_payment():
    if request.method == 'POST':
        # Nhận thông tin thanh toán từ yêu cầu POST
        payment_data = request.get_json()
        # amount = payment_data.get('amount')
        amount = 10000000

        # Tạo orderId và requestId
        order_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        # Cấu hình thông tin MoMo
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        access_key = "F8BBA842ECF85"
        secret_key = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        order_info = "Thanh chi phi kham benh"
        redirect_url = "/"  # Thay đổi URL redirect tại đây
        ipn_url = "https://your-ipn-url.com"  # Thay đổi URL IPN tại đây

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
        print(response.json())
        # Xử lý kết quả trả về từ MoMo
        if response.status_code == 200:
            response_data = response.json()
            if 'payUrl' in response_data:
                # Nếu thành công, trả về URL thanh toán cho frontend
                return jsonify({'payUrl': response_data['payUrl']})
            else:
                return jsonify({'error': 'Failed to process payment'}), 500
        else:
            return jsonify({'error': 'Failed to communicate with MoMo'}), 500

    else:
        return jsonify({'error': 'Invalid request method'}), 405


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


if __name__ == '__main__':
    with app.app_context():
        from clinicapp import admin

        app.run(debug=True)

