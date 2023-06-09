from django.contrib.auth.forms import AuthenticationForm
from django.forms import *
from .models import *


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = [
            'last_name', 'first_name', 'middle_name',
            'birthday', 'parent_name', 'parent_number',
            'address', 'email', 'social_category', 'school', 'petition_doc',
            'agreement_doc', 'sms_agreement_doc', 'comment',
            'passport_copy_parent', 'passport_or_birth_copy', 'direction'
        ]
        widgets = {
            'last_name': TextInput(
                attrs={'class': 'form-control text-capitalize', 'id': 'lastNameInput', 'placeholder': 'Фамилия'}),
            'first_name': TextInput(
                attrs={'class': 'form-control text-capitalize', 'id': 'firstNameInput', 'placeholder': 'Имя'}),
            'middle_name': TextInput(
                attrs={'class': 'form-control text-capitalize', 'id': 'middleNameInput', 'placeholder': 'Отчество'}),
            'birthday': DateInput(attrs={'class': 'form-control', 'id': 'birthInput', 'placeholder': 'дд.мм.гггг'}),
            'parent_name': TextInput(attrs={'class': 'form-control text-capitalize', 'id': 'parentNameInput',
                                            'placeholder': 'Иванов Иван Иванович'}),
            'parent_number': TextInput(
                attrs={'class': 'form-control', 'id': 'phoneInput', 'placeholder': '+7(000)-000-00 00'}),
            'address': TextInput(attrs={'class': 'form-control', 'id': 'addressInput',
                                        'placeholder': 'ул.Ленина 10, кв.10, г.Москва, Московская обл.'}),
            'email': EmailInput(attrs={'class': 'form-control', 'id': 'emailInput', 'placeholder': 'name@example.com'}),
            'social_category': Select(attrs={'class': 'form-select', 'id': 'socialInput'}),
            'school': TextInput(attrs={'class': 'form-control text-capitalize',
                                       'id': 'schoolInput', 'placeholder': 'МКОУ СОШ №0'}),
            'agreement_doc': FileInput(attrs={'class': 'form-control', 'id': 'AgreeFile'}),
            'sms_agreement_doc': FileInput(attrs={'class': 'form-control', 'id': 'SMSAgreeFile'}),
            'petition_doc': FileInput(attrs={'class': 'form-control', 'id': 'petitionFile'}),
            'passport_copy_parent': FileInput(attrs={'class': 'form-control', 'id': 'passportFile'}),
            'passport_or_birth_copy': FileInput(attrs={'class': 'form-control', 'id': 'passportOrBirthFile'}),
            'direction': Select(attrs={'class': 'form-select', 'id': 'directionInput'}),
            'comment': Textarea(attrs={'class': 'form-control', 'id': 'commentInput', 'style': 'height: 165px'})
        }


class AddStudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['adding_document', 'adding_date', 'group']
        widgets = {
            'adding_document': FileInput(attrs={'class': 'form-control', 'id': 'addingFile'}),
            'adding_date': DateInput(attrs={'class': 'form-control', 'id': 'addingDateInput', 'type': 'date'}),
            'group': Select(attrs={'class': 'form-select', 'id': 'groupInput'}),
        }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True


class AddPaidForm(ModelForm):
    class Meta:
        model = PaidGroupEnroll
        fields = ['paid_group', 'paid_date', 'paid_doc', 'paid_contract']
        widgets = {
            'paid_group': Select(attrs={'class': 'form-select', 'id': 'paidGroupInput'}),
            'paid_doc': FileInput(attrs={'class': 'form-control', 'id': 'paidFile'}),
            'paid_contract': FileInput(attrs={'class': 'form-control', 'id': 'paidContract'}),
            'paid_date': DateInput(attrs={'class': 'form-control', 'id': 'paidDateInput', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True


class DeleteStudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['delete_date', 'delete_document', 'delete_comment']
        widgets = {
            'delete_document': FileInput(attrs={'class': 'form-control', 'id': 'deleteFile'}),
            'delete_date': DateInput(attrs={'class': 'form-control', 'id': 'deleteDateInput', 'type': 'date'}),
            'delete_comment': TextInput(attrs={'class': 'form-control', 'id': 'commentInput'}),
        }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True


class DeletePaidForm(ModelForm):
    class Meta:
        model = PaidGroupEnroll
        fields = ['paid_delete_date', 'paid_delete_doc', 'paid_delete_comment', 'paid_group']
        widgets = {
            'paid_delete_doc': FileInput(attrs={'class': 'form-control', 'id': 'deletePaidFile'}),
            'paid_delete_date': DateInput(attrs={'class': 'form-control', 'id': 'deletePaidDateInput', 'type': 'date'}),
            'paid_delete_comment': TextInput(attrs={'class': 'form-control', 'id': 'commentPaidInput'}),
            'paid_group': Select(attrs={'class': 'form-select', 'id': 'paidDeleteFromInput'}, )
        }

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        if type(self.instance) is Student:
            self.fields['paid_group'].queryset = PaidGroup.objects.filter(student=self.instance)
        else:
            pass

        for key in self.fields:
            self.fields[key].required = True


class AuthUserForm(AuthenticationForm, ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class LoadTableForm(ModelForm):
    class Meta:
        model = LoadTable
        fields = ['file_name']
        widgets = {
            'file_name': FileInput(attrs={
                'id': 'load-file', 'class': 'form-control'
            })
        }
