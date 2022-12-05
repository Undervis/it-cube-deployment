var appMain = new Vue({
    el: '#main-app',
    data: {
        students: []
    },
    created: function() {
        if(window.location.pathname == '/') {
            this.getStudents(window.location.hash.replace('#', ''));
            window.addEventListener('hashchange', function(){
                let filter = this.window.location.hash.replace('#', '');
                appMain.getStudents(filter);
            });
        }
    },
    methods: {
        getStudents: function(filter) {
            if(filter === undefined){
                filter = ""
            }
            axios.get('/api/students' + "?" + filter)
            .then((response) => {
                this.students = response.data
            })
            .catch((error) => {
                console.log(error)
            })
        },
        openStudentCard: function(id) {
            window.open('/student/' + id, '_self')
        }
    }
})

var appJournal = new Vue({
    el: '#journal-app',
    data: {
        months: ['Сентябрь', "Октябрь", "Ноябрь", "Декабрь", "Январь", "Февраль", "Март", "Апрель", "Май"],
        user: {},
        students: [],
        group_tb: [],
        group_dates: [],
        group_marks: [],
        group_themes: [],
        cols: [1, 2, 3, 4, 5, 6, 7, 8, 9],
        tabIndex: 1,
        activeMonth: "Сентябрь"
    },
    created: function() {
        this.getJournal(window.location.hash.replace('#', ''));
        window.addEventListener('hashchange', function(){
            let filter = this.window.location.hash.replace('#', '');
            appJournal.getJournal(filter);
        });
    },
    methods:{
        getJournal: function(filter) {
            if(filter === undefined){filter = ""}
            axios.get('/api/journal/' + this.activeMonth + "?" + filter)
            .then((response) => {
                this.students = response.data.students;
                this.group_marks = response.data.group_marks.students_marks;
                this.group_dates = response.data.group_marks.dates;
                this.group_themes = response.data.group_marks.themes;
                this.group_tb = response.data.group_tb;
            })
            .catch((error) => {
                console.log(error)
            })
        },
        changeMonth: function(month) {
            this.activeMonth = month;
            let filter = window.location.hash.replace('#', '')
            this.getJournal(filter);
        }
    }
})