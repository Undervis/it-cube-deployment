from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from openpyxl import load_workbook


def home(request):
    directions = Direction.objects.all()
    users = User.objects.all()
    groups = Group.objects.all()
    paid_groups = PaidGroup.objects.all()
    user = request.user

    if request.GET.get('direction'):
        students = Student.objects.filter(direction=Direction.objects.get(pk=request.GET.get('direction')))
    elif request.GET.get('group'):
        students = Student.objects.filter(group=Group.objects.get(pk=request.GET.get('group')))
    elif request.GET.get('paidgroup'):
        students = Student.objects.filter(paid_group=PaidGroup.objects.get(pk=request.GET.get('paidgroup')))
    elif request.GET.get('teacher'):
        group = Student.objects.filter(group__teacher=User.objects.get(pk=request.GET.get('teacher')))
        students = group.union(Student.objects.filter(paid_group__teacher=User.objects.get(pk=request.GET.get('teacher'))))
    else:
        students = Student.objects.all()

    return render(request, 'home.html', {'students': students,
                                         'directions': directions,
                                         'teachers': users, 'user': user,
                                         'groups': groups, 'paid_groups': paid_groups})


def get_xlsx():
    wb = load_workbook('static/2022-05-30 Zaiavka.xlsx')
    sheet = wb.get_sheet_by_name('Sheet')
    print(sheet['A1'].value)


def get_student(request, pk):
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


def edit_student(request, pk):
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


def create(request):
    errors = ''
    if request.POST:
        student_form = StudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            student_form.save()

            student = Student.objects.last()

            set_status(student)

            return redirect('home')
        else:
            errors = student_form.errors
    else:
        student_form = StudentForm

    return render(request, 'create.html', {'student_form': student_form, 'errors': errors})
