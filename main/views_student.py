from .models import Student
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied


def get_students_manager(request):
    if request.GET.get('direction'):
        students = Student.objects.filter(direction=Direction.objects.get(pk=request.GET.get('direction')))
    elif request.GET.get('group'):
        students = Student.objects.filter(group=Group.objects.get(pk=request.GET.get('group')))
    elif request.GET.get('paidgroup'):
        students = Student.objects.filter(
            paid_group=PaidGroup.objects.get(id=request.GET.get('paidgroup')))
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

def get_paid_groups(students, mode: int):
    if mode == 0:
        for s in students:
            s.paid_groups = PaidGroupEnroll.objects.filter(student=s)
            s.paid_status = False
            for pg in s.paid_groups:
                if pg.paid_status == 0:
                    s.paid_status = True

        return students
    if mode == 1:
        students.paid_groups = PaidGroupEnroll.objects.filter(student=students)
        return students

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
    student = get_paid_groups(student, 1)

    if request.FILES.get('adding_document'):
        add_student_form = AddStudentForm(request.POST, request.FILES, instance=student)
        if add_student_form.is_valid():
            add_student_form.save()
            student.status = 0
            student.direction = student.group.direction
            student.save()

            redirect('/student/' + str(pk))
        else:
            messages.add_message(request, messages.WARNING, add_student_form.errors.as_p)
    else:
        add_student_form = AddStudentForm

    if request.FILES.get('paid_doc'):
        paid_student_form = AddPaidForm(request.POST, request.FILES)
        if paid_student_form.is_valid():
            paid_exist = PaidGroupEnroll.objects.filter(
                paid_group__group_name=paid_student_form.cleaned_data.get('paid_group')).exists()
            if not paid_exist:
                paid_enroll = paid_student_form.save(commit=False)
                paid_enroll.student = student
                paid_enroll.status = 0
                paid_enroll.save()
                student.status = 0
                student.save()

                redirect('/student/' + str(pk))
            else:
                messages.add_message(request, messages.WARNING, 'Этот ученик уже есть в группе')
    else:
        paid_student_form = AddPaidForm

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
        paid_enroll = PaidGroupEnroll.objects.get(paid_group__id=request.POST.get('paid_group'))
        paid_delete_student_form = DeletePaidForm(request.POST, request.FILES, instance=paid_enroll)
        if paid_delete_student_form.is_valid():
            paid_enroll = paid_delete_student_form.save(commit=False)
            print(paid_enroll)
            paid_enroll.paid_status = 1
            paid_enroll.save()
            if not student.group or student.delete_document:
                student.status = 2
                student.save()

            redirect('/student/' + str(pk))
        else:
            messages.add_message(request, messages.WARNING, paid_delete_student_form.errors.as_p)
    else:
        paid_delete_student_form = DeletePaidForm(instance=student)

    return render(request, 'student/student.html', {'student': student,
                                                    'user_can_edit': user_can_edit,
                                                    'user_can_delete': user_can_delete,
                                                    'user_can_adding': user_can_adding,
                                                    'student_form': add_student_form,
                                                    'paid_form': paid_student_form,
                                                    'delete_form': delete_student_form,
                                                    'paid_delete_form': paid_delete_student_form,
                                                    'errors': errors})


@login_required(login_url='/login')
def edit_student(request, pk):
    if not request.user.has_perm('main.can_edit'):
        raise PermissionDenied
    errors = ''
    student = get_object_or_404(Student, pk=pk)
    if request.POST:
        student_form = StudentForm(request.POST, request.FILES, instance=student)
        if student_form.is_valid():
            student_form.save()

            return redirect('/student/' + str(pk))
        else:
            errors = student_form.errors
    else:
        student_form = StudentForm(instance=student)

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
            student.save()

            return redirect('home')
        else:
            errors = student_form.errors
    else:
        student_form = StudentForm

    return render(request, 'create.html', {'student_form': student_form, 'errors': errors})