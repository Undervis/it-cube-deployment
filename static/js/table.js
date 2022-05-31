$(document).ready(function () {
    $('#looking-fields').children('.form-check').children('input').each(function () {
        let $data = $(this).attr('data-field')
        let $table = $('#main-table')
        if ($.cookie($data) !== null) {
            if ($.cookie($data) === 'true') {
                $(this).prop('checked', true)
                $table.children('thead').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).removeAttr('hidden')
                    }
                })
                $table.children('tbody').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).removeAttr('hidden')
                    }
                })
            } else {
                $(this).prop('checked', false)
                $table.children('thead').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).prop('hidden', true)
                    }
                })
                $table.children('tbody').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).prop('hidden', true)
                    }
                })
            }
        }
        $(this).on('change', function () {
            if ($(this).prop('checked') === true) {
                $.cookie($data, true, {expires: 365});
                $table.children('thead').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).removeAttr('hidden')
                    }
                })
                $table.children('tbody').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).removeAttr('hidden')
                    }
                })
            } else {
                $.removeCookie($data)
                $.cookie($data, false, {expires: 365});
                $table.children('thead').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).prop('hidden', true)
                    }
                })
                $table.children('tbody').children('tr').children('td').each(function () {
                    if ($(this).attr('data-field') === $data) {
                        $(this).prop('hidden', true)
                    }
                })
            }
        })
    })
});