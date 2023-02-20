import datetime

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    is_teacher = models.BooleanField('Педагог')
    last_name = models.CharField('Фамилия', max_length=20)
    first_name = models.CharField('Имя', max_length=20)
    middle_name = models.CharField('Отчество', max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField('Фото', upload_to='photos', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Direction(models.Model):
    direction_name = models.CharField('Название направления', max_length=96)
    teachers = models.ManyToManyField(User, verbose_name='Педагоги')

    class Meta:
        verbose_name_plural = 'Направления'

    def __str__(self):
        return self.direction_name


class PaidGroup(models.Model):
    group_name = models.CharField('Название группы', max_length=64)
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, verbose_name='Направление')
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Педагог')

    class Meta:
        verbose_name_plural = 'Платные группы'
        verbose_name = 'платную группу'

    def __str__(self):
        return self.group_name


class PaidGroupEnroll(models.Model):
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    paid_group = models.ForeignKey(PaidGroup, on_delete=models.PROTECT)
    paid_status_choice = [
        (0, 'Зачислен'),
        (1, 'Отчислен'),
        (2, 'Резерв')
    ]
    paid_status = models.IntegerField("Статус", choices=paid_status_choice, default=0)
    paid_doc = models.FileField('Приказ зачисления внебюджет', upload_to='documents', blank=True)
    paid_contract = models.FileField('Договор', upload_to='documents/paid_contracts', blank=True)
    paid_date = models.DateField('Дата зачисления внебюджет', blank=True, null=True)
    paid_delete_doc = models.FileField('Приказ отчисления внебюджет', upload_to='documents', blank=True)
    paid_delete_date = models.DateField('Дата отчисления внебюджет', blank=True, null=True)
    paid_delete_comment = models.CharField('Причина отчисления внебюджет', max_length=128, default='')

    def __str__(self):
        return self.paid_group.group_name


class Group(models.Model):
    group_name = models.CharField('Название группы', max_length=64)
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, verbose_name='Направление')
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Педагог')

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'группу'

    def __str__(self):
        return self.group_name


class Student(models.Model):
    student_status = [
        (0, 'Зачислен'),
        (1, 'Отчислен'),
        (2, 'Резерв')
    ]

    student_social_category = [
        (0, 'Отсутствует'),
        (1, 'Многодетная семья'),
        (2, 'Неполная семья'),
        (3, 'Инвалидность'),
        (4, 'Ограниченные возможности здоровья')
    ]

    last_name = models.CharField("Фамилия", max_length=20)
    first_name = models.CharField("Имя", max_length=20)
    middle_name = models.CharField("Отчество", max_length=20)
    birthday = models.DateField('Дата рождения')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Группа', blank=True, null=True)
    parent_name = models.CharField('ФИО Родителя', max_length=96)
    parent_number = PhoneNumberField('Номер телефона родителя')
    address = models.CharField('Адрес проживания', max_length=96, blank=True, null=True)
    email = models.EmailField('Электронный адрес')
    status = models.IntegerField("Статус", choices=student_status, default=2)
    social_category = models.IntegerField("Социальная категория", choices=student_social_category, default=0)
    school = models.CharField(max_length=128, verbose_name='Школа', blank=True, null=True)
    petition_date = models.DateTimeField("Дата подачи заявления", blank=True, null=True)
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, verbose_name='Направление')
    comment = models.TextField('Комментарий', blank=True, null=True)

    # Зачисление/отчисление
    adding_date = models.DateField('Дата зачисления', blank=True, null=True)
    delete_date = models.DateField('Дата отчисления', blank=True, null=True)
    adding_document = models.FileField('Приказ зачисления', upload_to='documents', blank=True)
    delete_document = models.FileField('Приказ отчисления', upload_to='documents', blank=True)
    delete_comment = models.CharField('Причина отчисления', max_length=128, default='')

    # Внебюджет
    paid_group = models.ManyToManyField(PaidGroup, verbose_name='Внебюджетная группа',
                                        blank=True, null=True, through=PaidGroupEnroll)

    # Основные документы
    petition_doc = models.FileField('Заявление на зачисление', upload_to='documents', blank=True)
    sms_agreement_doc = models.FileField('Расписка на получение SMS сообщений', upload_to='documents',
                                         blank=True)
    agreement_doc = models.FileField('Согласие на обработку персональных данных', upload_to='documents',
                                     blank=True)
    passport_copy_parent = models.FileField('Копия паспорта родителя', upload_to='documents', blank=True)
    passport_or_birth_copy = models.FileField('Копия паспорта/свидетельства о рождении ребёнка',
                                              upload_to='documents', blank=True)

    class Meta:
        verbose_name_plural = 'Учащиеся'
        verbose_name = 'учащийся'
        permissions = [
            ('can_edit', 'Can edit students'),
            ('can_adding', 'Can adding students'),
            ('can_delete', 'Can delete students')
        ]

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.middle_name

    def get_age(self):
        today = datetime.date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))


class LoadTable(models.Model):
    file_name = models.FileField(upload_to='tables')
