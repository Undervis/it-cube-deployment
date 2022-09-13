$(document).ready(function () {
    $('.month').each(function () { // Селектор месяцев
        $(this).removeClass('active')
        if ($(this).text() === $.cookie('last_month')){
            $(this).addClass('active')
        }
        $(this).on('click', function () {
            $('.month').each(function () {
                $(this).removeClass('active')
            });
            $(this).addClass('active');
            $.cookie('last_month', $(this).text(), {expires: 300})
            load_data()
        })
    })

    // Переключение тб и журнала
    $('.top-panel').each(function () {
        $(this).on('click', function () {
            $('.top-panel').each(function () {
                $(this).removeClass('active')
            });
            $(this).addClass('active');
            if ($('.top-panel.active').attr('data-index') === '1') {
                $('#table-marks').prop('hidden', false)
                $('#table-themes').prop('hidden', false)
                $('#table-tb').prop('hidden', true)
            } else {
                $('#table-marks').prop('hidden', true)
                $('#table-themes').prop('hidden', true)
                $('#table-tb').prop('hidden', false)
                load_tb()
            }
        })
    })

    if (document.location.href.indexOf('journal') > 0) {
        $('input').each(function () {
            $(this).on('change', function () {
                $('#warning-text').prop('hidden', false)
            })
        })
        $('select').each(function () {
            $(this).on('change', function () {
                $('#warning-text').prop('hidden', false)
            })
        })
    }

    // Заполнение тб именами
    for (let row = 1; row <= 16; row++) {
        $('#tb-name-' + row).text($('#name-' + row).text())
    }

    // Обновление полей ввода даты и часов
    $('.journal-date').each(function () {
        $(this).on('change', function () {
            $('#theme-date-' + $(this).attr('data-col')).val($(this).val())
            if ($(this).val() === '') {
                $('#theme-time-' + $(this).attr('data-col')).val('')
            } else {
                $('#theme-time-' + $(this).attr('data-col')).val('2')
            }
        })
    })

    // Загрузка данных в таблицы
    let load_data = function () {
        // Очистка полей
        $('.journal-date').each(function () {
            $(this).val('')
        })
        $('.journal-tb').each(function () {
            $(this).val('')
        })
        $('.journal-mark').each(function () {
            $(this).children('option').prop('selected', false)
        })


        try {
            // Парсинг данных
            let actual_data_text = $('.loaded-table-data[data-month="' + $('a.month.active').text() + '"]').text()
            actual_data_text = actual_data_text.replaceAll("'", '"')
            let actual_data = JSON.parse(actual_data_text)

            // Вывод данных
            for (let row = 1; row <= 16; row++) {
                $('#theme-date-' + row).val(actual_data.themes[row - 1].date)
                $('#theme-time-' + row).val(actual_data.themes[row - 1].time)
                $('#theme-' + row).val(actual_data.themes[row - 1].theme)

                $('#date-' + row).val(actual_data.dates[row - 1])
                for (let col = 1; col <= 16; col++) {
                    try {
                        let mark = $('#mark-' + row + '-' + col + " option[value=" + actual_data.students[row - 1].marks[col - 1] + "]")
                        mark.prop('selected', true)
                    } catch (e) {
                    }
                }
            }
        } catch (e) {

        }
    }

    // Загрузка данных таблицы техники безопасности
    let load_tb = function () {
        try {
            // Парсинг данных
            let tb_data_text = $('#loaded-tb-data').text()

            tb_data_text = tb_data_text.replaceAll("'", '"')
            let tb_data = JSON.parse(tb_data_text)
            tb_data = tb_data.tb
            console.log(JSON.stringify(tb_data[0]['date_bs']))

            for (let row = 1; row <= 16; row++) {
                $("#tb-bs-date-" + row).val(tb_data[row - 1]['date_bs'])
                $("#tb-bs-theme-" + row).val(tb_data[row - 1]['theme_bs'])
                $("#tb-pdd-date-" + row).val(tb_data[row - 1]['date_pdd'])
                $("#tb-pdd-theme-" + row).val(tb_data[row - 1]['theme_pdd'])
            }
        } catch (e) {
            console.log(e)
        }
    }

    // Первоначальная загрузка данных
    load_data()

    // Кнопка скачать
    setInterval(function () {
        $("#download-table").attr('href', '/static/journal/' + $('.list-item.group.active').text() + '.xlsx')
    }, 1000)

    // Кнопка сохранить
    $('#export-table').on('click', function () {
        $('#warning-text').prop('hidden', true)
        let journal = {};
        journal.group = $('.list-item.group.active').text();
        journal.month = $('a.month.active').text();
        journal.dates = [];
        journal.students = [];
        journal.themes = [];
        journal.tb = [];
        for (let row = 1; row <= 16; row++) {
            journal.dates.push($('#date-' + row).val())
            journal.themes.push({
                'date': $('#theme-date-' + row).val(),
                'time': $('#theme-time-' + row).val(),
                'theme': $('#theme-' + row).val()
            })
            journal.tb.push({
                'name': $('#tb-name-' + row).text(),
                'date-bs': $('#tb-bs-date-' + row).val(),
                'theme-bs': $('#tb-bs-theme-' + row).val(),
                'date-pdd': $('#tb-pdd-date-' + row).val(),
                'theme-pdd': $('#tb-pdd-theme-' + row).val()
            })
            let $studentName = $("#name-" + row)
            if ($studentName.text() === '') {
                continue
            }
            if ($studentName.attr('data-bs-toggle') === 'tooltip') {
                journal.students.push({
                    name:
                        $studentName.text() + " (" + $studentName.attr('data-bs-title') + ')', marks: []
                });
            } else {
                journal.students.push({name: $studentName.text(), marks: []});
            }
            for (let col = 1; col <= 16; col++) {
                journal.students[row - 1].marks.push($('#mark-' + row + '-' + col).val());
            }
        }

        let $toastText = $('#toast-text')

        // Отправка собранных данных
        $.ajax({
            data: {'data': JSON.stringify(journal)},
            url: '/load-journal',
            type: "POST",
            success: function (response) {
                let toast = new bootstrap.Toast($('#liveToast'));
                $toastText.removeClass('text-danger')
                $toastText.addClass('text-primary');
                $toastText.text('Данные успешно сохранены, страница будет перезагружена')
                toast.show()
                setInterval(function () {
                    window.location.reload();
                }, 3000)
            },
            error: function (response) {
                let toast = new bootstrap.Toast($('#liveToast'));
                $toastText.removeClass('text-primary');
                $toastText.addClass('text-danger');
                $toastText.text('Ошибка при сохранении данных')
                toast.show()
            }
        });
        return false;
    })

    // Всплывающие подсказки Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});