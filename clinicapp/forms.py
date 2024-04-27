from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, DateField, FileField, EmailField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, NumberRange, Regexp

from clinicapp.models import Gender


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
