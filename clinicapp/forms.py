import re

from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, DateField, FileField, EmailField
from flask_wtf import FlaskForm
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, DataRequired, EqualTo, Email, ValidationError

from clinicapp import dao
from clinicapp.models import Gender, MedicineCategory, User


def unique_email(form, field):
    if User.query.filter(User.email == field.data, User.id != form.user_id.data).first():
        raise ValidationError('Email đã dược sử dụng')


def unique_cid(form, field):
    if User.query.filter(User.cid == field.data, User.id != form.user_id.data).first():
        raise ValidationError('Căn cước đã được sử dụng')


def unique_phone(form, field):
    if User.query.filter(User.phone == field.data, User.id != form.user_id.data).first():
        raise ValidationError('SĐT đã dược sử dụng')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=1, max=15)], render_kw={"placeholder": "Tên đăng nhập"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mật khẩu"})
    submit = SubmitField("Đăng nhập")


class RegisterUser(FlaskForm):
    name = StringField("Họ và tên: ", validators=[InputRequired()])
    cid = StringField("CMND / CCCD: ", validators=[InputRequired(), Length(min=9, max=12), Regexp('^[0-9]*$', message="CCCD chỉ có số")])
    gender = SelectField("Giới tính: ", validators=[InputRequired()], default=Gender.MALE)
    address = StringField("Địa chỉ: ", validators=[InputRequired()])
    dob = DateField("Ngày sinh: ", validators=[InputRequired()], format="%Y-%m-%d")
    avatar = FileField("Ảnh đại diện: ")
    email = EmailField("Email: ")
    phone = StringField("Số điện thoại: ", validators=[Length(max=11)])
    submit = SubmitField("Thêm")


# class MedicineForm(FlaskForm):
#     medicine_id = HiddenField()
#     medicine_name = StringField("Thuốc")
#     dosage = StringField("Cách dùng")
#     quantity = IntegerField("Số lượng", default=1)
#     unit = SelectField("Đơn vị", coerce=int)
#     delete_medicine = SubmitField("Xóa thuốc")
#
#     def __init__(self, *args, **kwargs):
#         super(MedicineForm, self).__init__(*args, **kwargs)
#         self.unit.choices = [(unit.id, unit.name) for unit in dao.get_units()]


class PrescriptionForm(FlaskForm):
    patient_cid = IntegerField("CCCD bệnh nhân", validators=[DataRequired(), Length(min=9, max=12), Regexp('^[0-9]*$', message="CCCD chỉ chứa số")])
    name = StringField("Họ tên", validators=[DataRequired()])
    diagnosis = TextAreaField("Chẩn đoán", validators=[DataRequired()])
    date = StringField("Ngày Khám", validators=[DataRequired()])
    appointment_id = IntegerField("Mã lịch hẹn", validators=[DataRequired()])
    advice = TextAreaField("Lời dặn")
    symptoms = StringField("Triệu chứng", validators=[DataRequired()])

    usage = TextAreaField("Cách dùng")
    quantity = IntegerField("Số lượng", default=1, validators=[NumberRange(min=1, max=50)])
    unit = SelectField("Đơn vị", coerce=int)
    medicine_type = SelectField("Loại thuốc", choices=[], coerce=int)
    medicine_name = SelectField("Tên thuốc", choices=[], coerce=int)

    submit = SubmitField("Tạo phiếu khám")


class EditProfileForm(FlaskForm):
    user_id = StringField()
    name = StringField('Họ tên', validators=[DataRequired()])
    cid = StringField('CMND', validators=[Length(min=9, max=12), unique_cid])
    dob = DateField('Ngày sinh', validators=[DataRequired()])
    phone = StringField('Điện thoại', validators=[DataRequired(), unique_phone])
    email = StringField('Email', validators=[Email(), unique_email])
    gender = SelectField('Giới tính', choices=[(gender.name, gender.value) for gender in Gender])
    address = StringField('Địa chỉ')
    submit = SubmitField('Lưu thay đổi')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu cũ', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu xác nhận không trùng khớp')])
    submit = SubmitField('Đổi mật khẩu')

    def validate_new_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError('Mật khẩu mới phải chứa ít nhất 8 ký tự.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Mật khẩu mới phải chứa ít nhất một chữ cái viết hoa.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Mật khẩu mới phải chứa ít nhất một chữ cái thường.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Mật khẩu mới phải chứa ít nhất một chữ số.')
        if not re.search(r'[\W_]', password):  # \W matches any non-alphanumeric character
            raise ValidationError('Mật khẩu mới phải chứa ít nhất một ký tự đặc biệt.')


class ChangeUsernameForm(FlaskForm):
    def validate_username(self, username):
        user = dao.get_user_by_username(username.data)
        if user is not None:
            raise ValidationError('Username đã tồn tại. Vui lòng chọn một username khác.')

    old_username = StringField('Username cũ:', validators=[DataRequired()])
    new_username = StringField('Username mới:', validators=[DataRequired(), Length(min=6, max=15), validate_username])
    submit = SubmitField('Đổi Username')


class ChangeAvatarForm(FlaskForm):
    avatar = FileField('Chọn hình ảnh', validators=[DataRequired()])
    submit = SubmitField('Đổi avatar')
