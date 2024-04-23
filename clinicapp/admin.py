import bcrypt
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from clinicapp.models import UserRole, User, Doctor, Nurse, Patient, Policy, Medicine, Unit, MedicineCategory
from clinicapp import app, db, utils
from flask_login import logout_user, current_user
from flask import redirect


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MyUserView(AuthenticatedView):
    column_list = ['id', 'name', 'phone', 'username', 'email', 'address', 'role']
    column_searchable_list = ['username', 'name', 'phone']
    column_editable_list = ['name', ]
    can_export = True
    column_filters = ['role']
    column_labels = {
        'id': 'ID',
        'name': 'Họ Tên',
        'phone': 'SĐT',
        'username': 'Tên người dùng',
        'email': 'Email',
        'address': 'Địa chỉ',
        'role': 'Vai trò',
    }

    def on_model_change(self, form, model, is_created):
        # Kiểm tra xem mật khẩu đã được thay đổi hay không
        if 'password' in form:
            password = form.password.data
            if password:
                # Băm mật khẩu mới và lưu vào model
                hashed_password = utils.hash_password(password)
                model.password = hashed_password
        super().on_model_change(form, model, is_created)

    def on_form_prefill(self, form, id):
        # Thực hiện cùng một băm mật khẩu khi hiển thị form để chỉnh sửa
        form.password.data = ''


class DoctorAdminView(ModelView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class NurseAdminView(ModelView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PatientAdminView(ModelView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PolicyAdminView(ModelView):
    column_list = ['name', 'value', 'admin']
    column_searchable_list = ['name', 'value']
    column_editable_list = ['name', 'value']
    column_labels = {
        'name': 'Tên Quy Định',
        'value': 'Giá Trị'
    }


class MedicineAdminView(ModelView):
    column_list = ['name', 'gia', 'usage', 'exp']
    column_searchable_list = ['name']
    column_editable_list = ['name', 'price', 'usage', 'exp']


class CategoryAdminView(ModelView):
    column_list = ['name', 'medicine']


# class MedicineCategoryAdminView(ModelView):
#     column_list = ['category', 'medicine']
#     column_labels = {'category': 'Danh Mục', 'medicine': 'Thuốc'}
#     column_searchable_list = ['category.name', 'medicine.name']
#     column_filters = ['category', 'medicine']
#     form_ajax_refs = {'medicine': {'fields': ['name']}}


class UnitAdminView(ModelView):
    column_list = ['id', 'name']


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(app, name='Clinic Website', template_mode='bootstrap4')
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(MyUserView(User, db.session))
admin.add_view(DoctorAdminView(Doctor, db.session, name="Bác sĩ"))
admin.add_view(NurseAdminView(Nurse, db.session, name="Y tá"))
admin.add_view(PatientAdminView(Patient, db.session, name="Bệnh nhân"))
admin.add_view(PolicyAdminView(Policy, db.session, name="Quy Định"))
admin.add_view(MedicineAdminView(Medicine, db.session, name="Thuốc"))
# admin.add_view(MedicineCategoryAdminView(MedicineCategory, db.session, name="Thuốc"))
admin.add_view(UnitAdminView(Unit, db.session, name="Đơn vị"))
admin.add_view(LogoutView(name='Đăng xuất'))
