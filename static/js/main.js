$(document).ready(function () {
    let $href = document.location.href

    $('.panel').each(function () {
        let $btn = $('.list-item')
        if ($href.indexOf('?') > 0) {
            $btn.removeClass('active')
        }
        $btn.each(function () {
            if ($(this).attr('href') === $href.substring($href.indexOf('?'))) {
                $(this).addClass('active')
            }
        })

    })

    $('.nav-item.menu').each(function () {
        if ($href.indexOf('direction') > 0) {
            $(this).children('a').removeClass('active')
            $('#dirs-tab').addClass('active')
            $('#homePanel').prop('hidden', false)
            $('#groupsPanel').prop('hidden', true)
            $('#teachersPanel').prop('hidden', true)
        }
        if (($href.indexOf('group') > 0) || ($href.indexOf('paidgroup') > 0)) {
            $(this).children('a').removeClass('active')
            $('#groups-tab').addClass('active')
            $('#homePanel').prop('hidden', true)
            $('#groupsPanel').prop('hidden', false)
            $('#teachersPanel').prop('hidden', true)
        }
        if ($href.indexOf('teacher') > 0) {
            $(this).children('a').removeClass('active')
            $('#teachers-tab').addClass('active')
            $('#homePanel').prop('hidden', true)
            $('#groupsPanel').prop('hidden', true)
            $('#teachersPanel').prop('hidden', false)
        }
        $(this).children('a').on('click', function () {
            if ($(this).hasClass('active')) {
                let $tab = $(this).attr('id')
                if ($tab === 'dirs-tab') {
                    $('#homePanel').prop('hidden', false)
                    $('#groupsPanel').prop('hidden', true)
                    $('#teachersPanel').prop('hidden', true)
                }
                if ($tab === 'teachers-tab') {
                    $('#homePanel').prop('hidden', true)
                    $('#groupsPanel').prop('hidden', true)
                    $('#teachersPanel').prop('hidden', false)
                }
                if ($tab === 'groups-tab') {
                    $('#homePanel').prop('hidden', true)
                    $('#groupsPanel').prop('hidden', false)
                    $('#teachersPanel').prop('hidden', true)
                }
            }

        })
    })

    // create none layout
    Isotope.Item.prototype._create = function () {
        // assign id, used for original-order sorting
        this.id = this.layout.itemGUID++;
        // transition objects
        this._transn = {
            ingProperties: {},
            clean: {},
            onEnd: {}
        };
        this.sortData = {};
    };

    Isotope.Item.prototype.layoutPosition = function () {
        this.emitEvent('layout', [this]);
    };

    Isotope.prototype.arrange = function (opts) {
        // set any options pass
        this.option(opts);
        this._getIsInstant();
        // just filter
        this.filteredItems = this._filter(this.items);
        // flag for initalized
        this._isLayoutInited = true;
    };

// layout mode that does not position items
    Isotope.LayoutMode.create('none');

    var qsRegex;
    var buttonFilter;

    var $grid = $('.grid').isotope({
        itemSelector: '.grid-item',
        layoutMode: 'none',
        transitionDuration: 0,
        filter: function () {
            var $this = $(this);
            var searchResult = qsRegex ? $this.text().match(qsRegex) : true;
            var buttonResult = buttonFilter ? $this.is(buttonFilter) : true;
            return searchResult && buttonResult;
        },
        getSortData: {
            name: '.name'
        },
        sortBy: name
    })

    let searchbar = $('.quicksearch')
    qsRegex = new RegExp(searchbar.val(), 'gi');
    $grid.isotope();

    var $quicksearch = searchbar.keyup(debounce(function () {
        qsRegex = new RegExp($quicksearch.val(), 'gi');
        $grid.isotope();
    }));

    searchbar.on('click', debounce(function () {
        qsRegex = new RegExp($quicksearch.val(), 'gi');
        $grid.isotope();
    }))

    $('#table-header').on('click', 'a', function () {
        let sortByValue = $(this).attr('data-sort');
        $grid.isotope({sortBy: sortByValue});
    })

// flatten object by concatting values
    function concatValues(obj) {
        var value = '';
        for (var prop in obj) {
            value += obj[prop];
        }
        return value;
    }

// debounce so filtering doesn't happen every millisecond
    function debounce(fn, threshold) {
        var timeout;
        threshold = threshold || 100;
        return function debounced() {
            clearTimeout(timeout);
            var args = arguments;
            var _this = this;

            function delayed() {
                fn.apply(_this, args);
            }

            timeout = setTimeout(delayed, threshold);
        };
    }

})