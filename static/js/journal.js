$(document).ready(function () {
    $('#export-table').on('click', function () {
        let journal = {};
        journal.month = $('a.month.active').text();
        journal.dates = [];
        for (let i = 1; i <= 16; i++) {
            journal.dates.push($('#date-' + i).val())
        }
        journal.students = [];
        for (let row = 1; row <= 16; row++){
            if ($("#name-"+row).text() === ''){ continue }
            journal.students.push({name: $('#name-'+row).text(), marks: []});
            for (let col = 1; col <= 16; col++){
                journal.students[row - 1].marks.push($('#mark-'+row+'-'+col).val());
            }
        }

        $.ajax({
            data: journal,
            url: '/load-journal',
            type: "POST",
            success: function (response){
                alert(response);
            },
            error: function (response){
                console.log(response)
            }
        });
        return false;
    })

});