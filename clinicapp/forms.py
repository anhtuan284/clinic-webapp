from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, DateField, FileField, EmailField
from flask_wtf import FlaskForm
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, DataRequired

from clinicapp import dao
from clinicapp.models import Gender, MedicineCategory


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
    advice = TextAreaField("Lời dặn")
    symptoms = StringField("Triệu chứng", validators=[DataRequired()])

    # medicines = FieldList(FormField(MedicineForm), min_entries=0)
    usage = TextAreaField("Cách dùng")
    quantity = IntegerField("Số lượng", default=1, validators=[NumberRange(min=1, max=50)])
    unit = SelectField("Đơn vị", coerce=int)
    medicine_type = SelectField("Loại thuốc", choices=[], coerce=int)
    medicine_name = SelectField("Tên thuốc", choices=[], coerce=int)
    # add_medicine = SubmitField("Thêm")

    submit = SubmitField("Tạo phiếu khám")

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if self.add_medicine.data:
                if not self.medicine_name:
                    self.medicine_name.errors.append("Thuốc không được bỏ trống.")
                    return False
            elif self.submit.data:
                if not self.diagnosis.data:
                    self.diagnosis.errors.append("Chưa đưa ra chẩn đoán cho bệnh nhân.")
                    return False
        return True
