// history.js - search and filter for the submission history page

$(document).ready(function() {

    function filterRows() {
        var searchText = $('#search').val().toLowerCase();
        var modeFilter = $('#mode_filter').val();

        $('#history_table tbody tr').each(function() {
            var $row = $(this);
            var rowMode = $row.data('mode');
            var rowText = $row.text().toLowerCase();

            var matchesSearch = (searchText === '' || rowText.indexOf(searchText) !== -1);
            var matchesMode = (modeFilter === 'all' || rowMode === modeFilter);

            if (matchesSearch && matchesMode) {
                $row.show();
            } else {
                $row.hide();
            }
        });
    }

    $('#search').on('input', filterRows);
    $('#mode_filter').on('change', filterRows);

});
