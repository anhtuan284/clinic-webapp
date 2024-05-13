import logging

from flask import redirect, request, url_for, flash
from flask_admin import BaseView, Admin
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.base import instance_state

from clinicapp import app, db, utils
from clinicapp.dao import get_medicines, get_categories, get_category_medicines, add_or_update_medicine, \
    delete_all_category_medicine_by_medicine_id, add_category_medicine, get_medicine_by_id, delete_medicine_by_id, \
    get_categories_by_medicine_id, get_units, delete_all_medicine_unit_by_medicine_id, add_medicine_unit, \
    get_medicine_unit_by_medicine_id, get_medicine_unit, get_unit_by_medicine_id, get_unit_name_and_quantity, \
    delete_admin_by_id, delete_doctor_by_id, delete_patient_by_id, delete_nurse_by_id, delete_cashier_by_id
from clinicapp.models import UserRole, User, Doctor, Nurse, Patient, Policy, Medicine, Unit, Category, MedicineUnit


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class AuthenticatedBaseView(BaseView):
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

    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            self.on_model_delete(model)
            if model.role == UserRole.ADMIN:
                delete_admin_by_id(model.id)
            if model.role == UserRole.DOCTOR:
                delete_doctor_by_id(model.id)
            if model.role == UserRole.PATIENT:
                delete_patient_by_id(model.id)
            if model.role == UserRole.NURSE:
                delete_nurse_by_id(model.id)
            if model.role == UserRole.CASHIER:
                delete_cashier_by_id(model.id)
            super().delete_model(model)
        except IntegrityError as ie:
            if ie.orig.args[0] == 1451:
                ieMessage = ie.orig.args[1].split()
                entry = ieMessage[len(ieMessage) - 1]
                flash(gettext('Không xoá được. %(error)s',
                              error="Dòng dữ liệu đã được tham chiếu bởi các dòng dữ liệu khác"), 'error')
            else:
                flash(gettext('Failed to delete record. %(error)s', error=str(ie)), 'error')
            return False
        except Exception as e:
            flash(gettext('Failed to delete record. %(error)s', error=str(e)), 'error')
            return False
        else:
            self.after_model_delete(model)

        return True


class DoctorAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class NurseAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PatientAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PolicyAdminView(AuthenticatedView):
    column_list = ['name', 'value', 'admin']
    column_searchable_list = ['name', 'value']
    column_editable_list = ['name', 'value']
    column_labels = {
        'name': 'Tên Quy Định',
        'value': 'Giá Trị'
    }

    def build_new_instance(self):
        model = self._manager.new_instance()

        # TODO: We need a better way to create model instances and stay compatible with
        model.admin_id = current_user.id
        state = instance_state(model)
        self._manager.dispatch.init(state, [], {})

        return model

    def create_model(self, form):
        """
            Create model from form.

            :param form:
                Form instance
        """
        try:
            model = self.build_new_instance()

            form.populate_obj(model)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            flash(gettext('Không tạo được dữ liệu. %(error)s', error=str(ex)), 'error')
            return False
        else:
            self.after_model_change(form, model, True)

        return model

    def delete_model(self, model):
        """
            Delete model.
            :param model:
                Model to delete
        """
        try:
            self.on_model_delete(model)
            super().delete_model(model)
        except IntegrityError as ie:
            if ie.orig.args[0] == 1451:
                ieMessage = ie.orig.args[1].split()
                entry = ieMessage[len(ieMessage) - 1]
                flash(gettext('Không xoá được. %(error)s',
                              error="Dòng dữ liệu đã được tham chiếu bởi các dòng dữ liệu khác"), 'error')

            else:
                flash(gettext('Failed to delete record. %(error)s', error=str(ie)), 'error')
            return False
        except Exception as e:
            flash(gettext('Failed to delete record. %(error)s', error=str(e)), 'error')
            return False
        else:
            self.after_model_delete(model)

        return True


class MedicineAdminView(AuthenticatedView):
    column_list = ['name', 'gia', 'usage', 'exp']
    column_searchable_list = ['name']
    column_editable_list = ['name', 'price', 'usage', 'exp']


class CategoryAdminView(AuthenticatedView):
    column_list = ['name', 'medicine']
    can_delete = False


# class MedicineCategoryAdminView(ModelView):
#     column_list = ['category', 'medicine']
#     column_labels = {'category': 'Danh Mục', 'medicine': 'Thuốc'}
#     column_searchable_list = ['category.name', 'medicine.name']
#     column_filters = ['category', 'medicine']
#     form_ajax_refs = {'medicine': {'fields': ['name']}}


class UnitAdminView(AuthenticatedView):
    column_list = ['id', 'name']
    can_delete = False


class StatsView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


class LogoutView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class ThuocView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        gia_bat_dau = request.args.get('gia_bat_dau')
        gia_ket_thuc = request.args.get('gia_ket_thuc')
        han_dung_bat_dau = request.args.get('han_dung_bat_dau')
        han_dung_ket_thuc = request.args.get('han_dung_ket_thuc')
        name = request.args.get('name')
        danhmuc_id = request.args.get('danhmuc_id')

        return self.render(
            'admin/thuoc.html',
            thuocs=get_medicines(
                price_bat_dau=gia_bat_dau,
                price_ket_thuc=gia_ket_thuc,
                han_dung_bat_dau=han_dung_bat_dau,
                han_dung_ket_thuc=han_dung_ket_thuc,
                name=name,
                category_id=danhmuc_id
            ),
            danhmucs=get_categories(),
            danhmucthuocs=get_category_medicines(),
            unit_name_and_quantity=get_unit_name_and_quantity()
        )

    @expose('/thuocs/', methods=['get', 'post'])
    def add_thuoc(self, id=None):
        units = get_units()
        if request.method.__eq__('POST'):
            id = request.form.get('id')
            gia = request.form.get('gia')
            name = request.form.get('name')
            cach_dung = request.form.get('cach_dung')
            han_su_dung = request.form.get('han_su_dung')
            ds_danh_muc = request.form.getlist('ds_danh_muc')
            dict_quantity_per_unit = {}
            # {
            #     1: 14,
            #     2: 1,
            #     3: 20
            #
            # }
            for u in units:
                dict_quantity_per_unit[u.id] = request.form.get(f"quantity-per-unit-{u.id}")

            thuocMoiId = add_or_update_medicine(
                id=id,
                price=gia,
                name=name,
                usage=cach_dung,
                exp=han_su_dung,
                dict_quantity_per_unit=dict_quantity_per_unit
            )

            for dm in ds_danh_muc:
                add_category_medicine(category_id=int(dm), medicine_id=thuocMoiId)

            return self.render('admin/them_thuoc.html', cates=get_categories(), units=units,
                               success_msg='Thêm thuốc thành công!!!')

        return self.render('admin/them_thuoc.html', cates=get_categories(), units=units)

    @expose('/thuocs/<id>', methods=['post'])
    def delete_thuoc(self, id):
        thuoc = get_medicine_by_id(id)

        if request.method.__eq__('POST'):
            try:
                delete_medicine_by_id(id)
                return redirect('/admin/thuocview/')
            except IntegrityError as ie:
                if ie.orig.args[0] == 1451:
                    return redirect(url_for('thuocview.index',
                                            err_msg=f'Mã lỗi: 149; Lỗi: Thuốc được xài trong phiếu khám nào đó rồi, nên không xoá được!!!'))
            except Exception as e:
                return redirect(url_for('thuocview.index', err_msg=str(e)))

    @expose('/thuocs/update/<id>', methods=['get', 'post'])
    def update_thuoc(self, id):
        thuoc = get_medicine_by_id(id)
        units = get_units()

        if request.method.__eq__('POST'):
            id = request.form.get('id')
            gia = request.form.get('gia')
            name = request.form.get('name')
            cach_dung = request.form.get('cach_dung')
            han_su_dung = request.form.get('han_su_dung')
            ds_danh_muc = request.form.getlist('ds_danh_muc')
            dict_quantity_per_unit = {}
            # {
            #     1: 14,
            #     2: 1,
            #     3: 20
            #
            # }
            for u in units:
                dict_quantity_per_unit[u.id] = request.form.get(f"quantity-per-unit-{u.id}")

            thuocMoiId = add_or_update_medicine(
                id=id,
                price=gia,
                name=name,
                usage=cach_dung,
                exp=han_su_dung,
                dict_quantity_per_unit=dict_quantity_per_unit
            )

            delete_all_category_medicine_by_medicine_id(thuocMoiId)
            delete_all_medicine_unit_by_medicine_id(thuocMoiId)
            for dm in ds_danh_muc:
                add_category_medicine(category_id=int(dm), medicine_id=thuocMoiId)
            for key in dict_quantity_per_unit.keys():
                if dict_quantity_per_unit[key]:
                    add_medicine_unit(unit_id=key, medicine_id=thuocMoiId, quantity=dict_quantity_per_unit[key])

            return redirect(url_for('thuocview.index', success_msg='Sửa thuốc thành công!!!'))

        print(get_medicine_unit_by_medicine_id(id))
        return self.render(
            'admin/them_thuoc.html',
            cates=get_categories(),
            thuoc=thuoc,
            currentcates=get_categories_by_medicine_id(id),
            units=units,
            currentunits=get_unit_by_medicine_id(id),
            current_med_units=get_medicine_unit_by_medicine_id(id)
        )


class MyDanhMucView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/danh_muc.html', danhmucs=get_categories())


class MyCategoryView(AuthenticatedView):
    column_list = ['id', 'name']
    can_delete = False

    form_widget_args = {
        'medicine_category': {
            'disabled': True
        },
        'created_date': {
            'disabled': True
        },
        'updated_date': {
            'disabled': True
        },
    }


admin = Admin(app, name='Clinic Website', template_mode='bootstrap4')

admin.add_view(ThuocView(name="Thuốc"))
admin.add_view(UnitAdminView(Unit, db.session, name="Đơn vị"))
admin.add_view(MyCategoryView(Category, db.session, name='Danh mục'))
admin.add_view(MyUserView(User, db.session))
admin.add_view(PolicyAdminView(Policy, db.session, name="Quy Định"))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
