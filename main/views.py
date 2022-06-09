import datetime

import openpyxl
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .models import *
from .forms import *
from openpyxl import load_workbook


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

        student.parent_name = worksheet.cell(i, 12).value.capitalize() + " " + \
                              worksheet.cell(i, 13).value.capitalize() + " " + \
                              worksheet.cell(i, 14).value.capitalize()

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
        student.direction = Direction.objects.get(direction_name=worksheet.cell(i, 24).value)
        if Student.objects.filter(last_name=student.last_name,
                                  first_name=student.first_name,
                                  middle_name=student.middle_name).count() == 0:
            student.save()


def load_file(request):
    filename = input('Путь к файлу: ')
    get_xlsx(filename)

    return redirect('/')


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
