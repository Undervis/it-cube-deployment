from .models import Group, PaidGroup
from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import openpyxl as xl
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required(login_url='/login')
def journal(request):
    group_name: str
    if not request.user.has_perm('main.can_edit'):
        user_can_edit = False
    else:
        user_can_edit = True

    user = request.user
    if Group.objects.all().count() or PaidGroup.objects.all().count():
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

        return render(request, 'journal.html',
                      {'students': students.order_by('last_name'), 'cols': cols, 'months': months,
                       'user_can_edit': user_can_edit, 'user': user, 'tables': tables,
                       'groups': groups, 'paid_groups': paid_groups, 'table_tb': table_tb})
    else:
        return render(request, 'page_error.html', {'error_title': 'Журнал не доступен',
                                                   'error_msg': 'Нет групп для заполнения журнала'})


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