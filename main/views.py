import datetime
import json

import openpyxl
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from it_cube.settings import BASE_DIR

from .models import *
from .forms import *
import openpyxl as xl


class MainLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('/')


class MainLogout(LogoutView):
    next_page = '/login'


def get_students_manager(request):
    if request.GET.get('direction'):
        students = Student.objects.filter(direction=Direction.objects.get(pk=request.GET.get('direction')))
    elif request.GET.get('group'):
        students = Student.objects.filter(group=Group.objects.get(pk=request.GET.get('group')))
    elif request.GET.get('paidgroup'):
        students = Student.objects.filter(paid_group=PaidGroup.objects.get(pk=request.GET.get('paidgroup')))
    elif request.GET.get('teacher'):
        group = Student.objects.filter(group__teacher=User.objects.get(pk=request.GET.get('teacher')))
        students = group.union(
            Student.objects.filter(paid_group__teacher=User.objects.get(pk=request.GET.get('teacher'))))
    else:
        students = Student.objects.all()

    return students.order_by('petition_date')


def get_students_teacher(request):
    if request.GET.get('group'):
        students = Student.objects.filter(
            group=Group.objects.get(pk=request.GET.get('group')), group__teacher=request.user)
    elif request.GET.get('paidgroup'):
        students = Student.objects.filter(
            paid_group=PaidGroup.objects.get(pk=request.GET.get('paidgroup')), paid_group__teacher=request.user)
    else:
        groups = Student.objects.filter(group__teacher=request.user)
        students = groups.union(Student.objects.filter(paid_group__teacher=request.user))

    return students.order_by('last_name')


@login_required(login_url='/login')
def journal(request):
    global students, table_tb
    group_name = ""
    if not request.user.has_perm('main.can_edit'):
        user_can_edit = False
    else:
        user_can_edit = True

    user = request.user
    if not user.userprofile.is_teacher:
        groups = Group.objects.all()
        paid_groups = PaidGroup.objects.all()
    else:
        groups = Group.objects.filter(teacher=user)
        paid_groups = PaidGroup.objects.filter(teacher=user)

    if not request.GET:
        first_group = groups.union(paid_groups).first()
        group_name = first_group.group_name
        students = Student.objects.filter(group=first_group)

    if request.GET.get('group'):
        group_name = Group.objects.get(id=request.GET.get('group')).group_name
        students = Student.objects.filter(group__id=request.GET.get('group'))
    if request.GET.get('paidgroup'):
        group_name = PaidGroup.objects.get(id=request.GET.get('paidgroup')).group_name
        students = Student.objects.filter(paid_group__pk=request.GET.get('paidgroup'))

    cols = [i for i in range(1, 17)]
    months = ['Сентябрь', "Октябрь", "Ноябрь", "Декабрь", "Январь", "Февраль", "Март", "Апрель", "Май"]

    tables = []
    table_tb = Table()
    try:
        if group_name.count("/") > 0:
            group_name = group_name.replace("/", ",")
        wb = xl.load_workbook(str(BASE_DIR) + '/static/journal/' + group_name + '.xlsx')
        for m in months:
            try:
                sheet = wb.get_sheet_by_name(m)
                table = Table()
                table.month = m
                for col in range(2, 18):
                    if sheet.cell(row=1, column=col).value:
                        table.dates.append(str(sheet.cell(row=1, column=col).value))
                    else:
                        table.dates.append("")
                row = 2
                while True:
                    if sheet.cell(row=row, column=1).value:
                        table.students.append({"name": str(sheet.cell(row=row, column=1).value), "marks": []})
                        for col in range(2, 18):
                            if sheet.cell(row=row, column=col).value == "НБ":
                                table.students[row - 2]["marks"].append(1)
                            elif sheet.cell(row=row, column=col).value == "Б":
                                table.students[row - 2]["marks"].append(2)
                            else:
                                table.students[row - 2]["marks"].append(0)
                        row += 1
                    else:
                        break
                for row in range(2, 18):
                    theme_date = sheet.cell(row=row, column=18).value
                    theme_time = sheet.cell(row=row, column=19).value
                    theme_title = sheet.cell(row=row, column=20).value
                    table.themes.append({"date": str(theme_date) if theme_date else "",
                                         "time": str(theme_time) if theme_time else "",
                                         "theme": str(theme_title) if theme_title else ""})
                tables.append(table)
            except:
                pass

        try:
            sheet_tb = wb.get_sheet_by_name('ТБ')
            table_tb = Table()

            for row in range(1, 18):
                if sheet_tb.cell(row=row + 1, column=1).value is not None:
                    date_bs = sheet_tb.cell(row=row + 1, column=2).value
                    theme_bs = sheet_tb.cell(row=row + 1, column=3).value
                    date_pdd = sheet_tb.cell(row=row + 1, column=5).value
                    theme_pdd = sheet_tb.cell(row=row + 1, column=6).value
                    table_tb.tb.append({
                        "name": sheet_tb.cell(row=row + 1, column=1).value,
                        "date_bs": date_bs if date_bs else "",
                        "theme_bs": theme_bs if theme_bs else "",
                        "date_pdd": date_pdd if date_pdd else "",
                        "theme_pdd": theme_pdd if theme_pdd else ""
                    })

        except:
            pass
    except:
        pass

    return render(request, 'journal.html', {'students': students.order_by('last_name'), 'cols': cols, 'months': months,
                                            'user_can_edit': user_can_edit, 'user': user, 'tables': tables,
                                            'groups': groups, 'paid_groups': paid_groups, 'table_tb': table_tb})


class Table:
    def __init__(self):
        self.month: str
        self.dates = []
        self.students = []
        self.themes = []
        self.tb = []


@csrf_exempt
@login_required(login_url='/login')
def load_json(request):
    if request.POST:
        table_data = json.loads(str(request.POST.get('data')))
        print(table_data)
        group_name = str(table_data['group'])
        if group_name.count('/') > 0:
            group_name = group_name.replace("/", ',')
        file_name = str(BASE_DIR) + '/static/journal/' + group_name + '.xlsx'
        try:
            wb = xl.load_workbook(file_name)
        except FileNotFoundError:
            xl.Workbook().save(file_name)
            wb = xl.load_workbook(file_name)

        try:
            sheet = wb.get_sheet_by_name(table_data['month'])
        except:
            sheet = wb.create_sheet(table_data['month'])

        sheet.cell(row=1, column=1).value = 'Фамилия Имя'
        sheet.column_dimensions['A'].width = 20
        for i in range(len(table_data['dates'])):
            sheet.cell(row=1, column=i + 2).value = table_data['dates'][i]

        for x in range(len(table_data['students'])):
            sheet.cell(row=x + 2, column=1).value = table_data['students'][x]['name']
            for y in range(len(table_data['students'][x]['marks'])):
                if table_data['students'][x]['marks'][y] == '0':
                    sheet.cell(row=x + 2, column=y + 2).value = ""
                elif table_data['students'][x]['marks'][y] == '1':
                    sheet.cell(row=x + 2, column=y + 2).value = "НБ"
                elif table_data['students'][x]['marks'][y] == '2':
                    sheet.cell(row=x + 2, column=y + 2).value = "Б"

        sheet.cell(row=1, column=18).value = 'Дата'
        sheet.cell(row=1, column=19).value = 'Часы'
        sheet.cell(row=1, column=20).value = 'Тема'
        sheet.column_dimensions['T'].width = 50
        for row in range(len(table_data['themes'])):
            sheet.cell(row=row + 2, column=18).value = table_data['themes'][row]['date']
            sheet.cell(row=row + 2, column=19).value = table_data['themes'][row]['time']
            sheet.cell(row=row + 2, column=20).value = table_data['themes'][row]['theme']

        try:
            sheet_tb = wb.get_sheet_by_name('ТБ')
        except:
            sheet_tb = wb.create_sheet('ТБ')

        sheet_tb.cell(row=1, column=1).value = "Фамилия имя"
        sheet_tb.cell(row=1, column=2).value = "Дата"
        sheet_tb.cell(row=1, column=3).value = "Тема"
        sheet_tb.cell(row=1, column=4).value = "Подпись"
        sheet_tb.cell(row=1, column=5).value = "Дата"
        sheet_tb.cell(row=1, column=6).value = "Тема"
        sheet_tb.cell(row=1, column=7).value = "Подпись"
        sheet_tb.column_dimensions['A'].width = 20
        sheet_tb.column_dimensions['C'].width = 30
        sheet_tb.column_dimensions['F'].width = 30

        for row in range(len(table_data['tb'])):
            sheet_tb.cell(row=row + 2, column=1).value = table_data['tb'][row]['name']
            sheet_tb.cell(row=row + 2, column=2).value = table_data['tb'][row]['date-bs']
            sheet_tb.cell(row=row + 2, column=3).value = table_data['tb'][row]['theme-bs']
            sheet_tb.cell(row=row + 2, column=5).value = table_data['tb'][row]['date-pdd']
            sheet_tb.cell(row=row + 2, column=6).value = table_data['tb'][row]['theme-pdd']

        wb.save(file_name)

    return JsonResponse({"msg": 'Success'})


@login_required(login_url='/login')
def home(request):
    if not request.user.has_perm('main.can_edit'):
        user_can_edit = False
    else:
        user_can_edit = True

    user = request.user
    directions = Direction.objects.all()
    users = User.objects.all()
    if not user.userprofile.is_teacher:
        groups = Group.objects.all()
        paid_groups = PaidGroup.objects.all()
    else:
        groups = Group.objects.filter(teacher=user)
        paid_groups = PaidGroup.objects.filter(teacher=user)

    if not user.userprofile.is_teacher:
        students = get_students_manager(request)
    else:
        students = get_students_teacher(request)

    return render(request, 'home.html', {'students': students,
                                         'user_can_edit': user_can_edit,
                                         'directions': directions,
                                         'teachers': users, 'user': user,
                                         'groups': groups, 'paid_groups': paid_groups})


def get_xlsx(file):
    wb = openpyxl.load_workbook(filename=file)
    worksheet = wb.active
    for i in range(2, worksheet.max_row):
        student = Student()
        student.petition_date = worksheet.cell(i, 3).value
        last_name = str(worksheet.cell(i, 6).value).capitalize()
        if last_name.upper().count('РЕЗЕРВ') > 0:
            last_name = last_name.upper().replace('РЕЗЕРВ', '').capitalize()
        student.last_name = last_name
        student.first_name = worksheet.cell(i, 7).value
        student.middle_name = worksheet.cell(i, 8).value
        student.birthday = worksheet.cell(i, 9).value
        print(i)
        student.parent_name = str(worksheet.cell(i, 12).value).capitalize() + " " + \
                              str(worksheet.cell(i, 13).value).capitalize() + " " + \
                              str(worksheet.cell(i, 14).value).capitalize()

        student.parent_number = worksheet.cell(i, 15).value
        student.email = worksheet.cell(i, 16).value
        for col in range(17, 22):
            if worksheet.cell(i, col).value is not None:
                if col == 17:
                    student.social_category = 0
                if col == 18:
                    student.social_category = 2
                if col == 19:
                    student.social_category = 1
                if col == 20:
                    student.social_category = 3
                if col == 21:
                    student.social_category = 4
        student.status = 1
        student.school = worksheet.cell(i, 11).value
        student.comment = worksheet.cell(i, 26).value
        student.direction = Direction.objects.get(direction_name=worksheet.cell(i, 24).value)
        if Student.objects.filter(last_name=student.last_name,
                                  first_name=student.first_name,
                                  middle_name=student.middle_name).count() == 0:
            student.save()
        else:
            student_old = Student.objects.filter(last_name=student.last_name,
                                                 first_name=student.first_name,
                                                 middle_name=student.middle_name).first()
            if student_old:
                student_old.comment = str(student.comment) + '\n' + str(student.direction.direction_name)
                student_old.save()


@login_required(login_url='/login')
def load_file(request):
    if not request.user.has_perm('main.can_edit'):
        raise PermissionDenied
    if request.POST:
        load_form = LoadTableForm(request.POST, request.FILES)
        if load_form.is_valid():
            load_form.save()

            filename = LoadTable.objects.last()
            get_xlsx(filename.file_name)
    else:
        load_form = LoadTableForm
    return render(request, 'load.html', {'load_form': load_form})


@login_required(login_url='/login')
def get_student(request, pk):
    if not request.user.has_perm('main.can_edit'):
        user_can_edit = False
    else:
        user_can_edit = True

    if not request.user.has_perm('main.can_delete'):
        user_can_delete = False
    else:
        user_can_delete = True

    if not request.user.has_perm('main.can_adding'):
        user_can_adding = False
    else:
        user_can_adding = True

    errors = ''
    student = get_object_or_404(Student, pk=pk)
    if request.FILES.get('adding_document'):
        add_student_form = AddStudentForm(request.POST, request.FILES, instance=student)
        if add_student_form.is_valid():
            add_student_form.save()
            student.status = 0
            student.direction = student.group.direction
            student.save()

            redirect('/student/' + str(pk))
        else:
            errors = add_student_form.errors
    else:
        add_student_form = AddStudentForm

    if request.FILES.get('paid_doc'):
        paid_student_form = AddPaidStudentForm(request.POST, request.FILES, instance=student)
        if paid_student_form.is_valid():
            paid_student_form.save()
            student.is_paid = True
            student.status = 0
            student.save()

            redirect('/student/' + str(pk))
    else:
        paid_student_form = AddPaidStudentForm

    if request.FILES.get('delete_document'):
        delete_student_form = DeleteStudentForm(request.POST, request.FILES, instance=student)
        if delete_student_form.is_valid():
            delete_student_form.save()
            student.status = 2
            student.save()

            redirect('/student/' + str(pk))
    else:
        delete_student_form = DeleteStudentForm

    if request.FILES.get('paid_delete_doc'):
        paid_delete_student_form = DeletePaidStudentForm(request.POST, request.FILES, instance=student)
        if paid_delete_student_form.is_valid():
            paid_delete_student_form.save()
            if not student.group or student.delete_document:
                student.status = 2
                student.save()

            redirect('/student/' + str(pk))
        else:
            errors = paid_delete_student_form.errors
    else:
        paid_delete_student_form = DeletePaidStudentForm

    return render(request, 'student/student.html', {'student': student,
                                                    'user_can_edit': user_can_edit,
                                                    'user_can_delete': user_can_delete,
                                                    'user_can_adding': user_can_adding,
                                                    'student_form': add_student_form,
                                                    'paid_form': paid_student_form,
                                                    'delete_form': delete_student_form,
                                                    'paid_delete_form': paid_delete_student_form,
                                                    'errors': errors})


def set_status(student):
    docs_count = 0
    if not student.petition_doc:
        docs_count += 1
    if not student.sms_agreement_doc:
        docs_count += 1
    if not student.agreement_doc:
        docs_count += 1
    if not student.passport_copy_parent:
        docs_count += 1
    if not student.passport_or_birth_copy:
        docs_count += 1

    if docs_count != 0:
        student.status = 1
    else:
        student.status = 3

    student.save()


@login_required(login_url='/login')
def edit_student(request, pk):
    if not request.user.has_perm('main.can_edit'):
        raise PermissionDenied
    errors = ''
    student = get_object_or_404(Student, pk=pk)
    can_edit = True
    if student.status == 2 or (student.status == 2 and student.paid_delete_doc):
        can_edit = False
    if student.status == 2 and not student.paid_delete_doc:
        can_edit = True
    if can_edit:
        if request.POST:
            student_form = StudentForm(request.POST, request.FILES, instance=student)
            if student_form.is_valid():
                student_form.save()

                set_status(student)

                return redirect('/student/' + str(pk))
            else:
                errors = student_form.errors
        else:
            student_form = StudentForm(instance=student)

    else:
        return redirect('/')

    return render(request, 'student/student_edit.html',
                  {'student_form': student_form, 'errors': errors, 'student': student})


@login_required(login_url='/login')
def create(request):
    if not request.user.has_perm('main.can_edit'):
        raise PermissionDenied
    errors = ''
    if request.POST:
        student_form = StudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            student_form.save()

            student = Student.objects.last()
            student.petition_date = datetime.datetime.now()
            set_status(student)

            return redirect('home')
        else:
            errors = student_form.errors
    else:
        student_form = StudentForm

    return render(request, 'create.html', {'student_form': student_form, 'errors': errors})
