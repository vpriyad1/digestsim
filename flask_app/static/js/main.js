// main.js - interactivity for the DigestSim input page

$(document).ready(function() {

    // Toggle enzyme selectors based on analysis mode
    $('input[name="analysis_mode"]').on('change', function() {
        var mode = $(this).val();
        if (mode === 'full_scan') {
            $('#enzyme_selectors').hide();
        } else {
            $('#enzyme_selectors').show();
        }
    });

    // Live validation of the DNA sequence box
    // Warn user if there are invalid characters
    $('#dna_sequence').on('input', function() {
        var seq = $(this).val().toUpperCase();
        var cleaned = seq.replace(/[^ATGC\s>\n]/g, '');
        var invalidCount = seq.length - cleaned.length;

        if (invalidCount > 0) {
            $(this).css('border-color', '#d97757');
        } else {
            $(this).css('border-color', '#d0d0d0');
        }
    });

    // Form submit validation
    $('#analysis_form').on('submit', function(e) {
        var seq = $('#dna_sequence').val().trim();
        if (seq.length === 0) {
            alert('Please enter a DNA sequence.');
            e.preventDefault();
            return false;
        }

        var mode = $('input[name="analysis_mode"]:checked').val();
        if (mode === 'specific') {
            var enzyme1 = $('#enzyme1').val();
            if (!enzyme1) {
                alert('Please select at least one enzyme, or switch to full scan mode.');
                e.preventDefault();
                return false;
            }
        }
    });

});
