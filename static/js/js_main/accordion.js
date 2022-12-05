let content = $('.accord-content')
content.attr('style', 'display: none;')

$(document).ready(function () {
    let trigger = $('.accord-trigger')
    let icon = $('.accord-icon')

    let icon_close = '/static/icons/icons/caret-right.svg'
    let icon_open = '/static/icons/icons/caret-down.svg'

    $('a.list-item.active').parent('.list-item').parent('.accord-content').before().toggle();
    $('a.list-item.group').each(function(){
        if ($(this).hasClass('active')){
            if (!$(this).parent().hasClass('accord-item')){
                let direction = $(this).parent('.panel-outer').attr('data-direction');
                $('.accord-item').each(function(){
                    if ($(this).attr('data-direction') === direction) {
                        $(this).children('a').children('img').attr('src', icon_open)
                    }
                })
            }
        }
    })

    trigger.on('click', function () {
        $(this).parent('.accord-item').next('.collapse').slideToggle(200);
        if ($(this).children(icon).attr('src') === icon_close) {
            $(this).children(icon).attr('src', icon_open)
        } else if ($(this).children(icon).attr('src') === icon_open) {
            $(this).children(icon).attr('src', icon_close)
        }
    })
})