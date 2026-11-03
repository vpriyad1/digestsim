// results.js - renders the visual cut map on the results page

$(document).ready(function() {

    var $map = $('#cut_map');
    if ($map.length === 0) {
        return;
    }

    var seqLength = parseInt($map.data('sequence-length'));
    var enzymes = $map.data('enzymes');  // jQuery auto-parses JSON from data-* attrs

    // Color palette for different enzymes
    var colors = ['#D85A30', '#0F6E56', '#534AB7', '#C26F1B', '#1F77B4', '#9467BD', '#8C564B'];

    // Draw the DNA bar
    $map.append('<div class="cut-map-bar"></div>');

    // Draw cut marks for each enzyme
    enzymes.forEach(function(enzyme, idx) {
        var color = colors[idx % colors.length];
        enzyme.cut_sites.forEach(function(pos) {
            var pct = (pos / seqLength) * 100;
            var $mark = $('<div class="cut-mark"></div>')
                .css({ left: pct + '%', backgroundColor: color });
            var $label = $('<div class="cut-label"></div>')
                .css('left', pct + '%')
                .text(pos);
            $map.append($mark);
            $map.append($label);
        });
    });

    // Build the legend
    var $legend = $('#cut_map_legend');
    enzymes.forEach(function(enzyme, idx) {
        var color = colors[idx % colors.length];
        var $item = $('<div class="legend-item"></div>');
        $item.append($('<span class="legend-dot"></span>').css('background-color', color));
        $item.append(document.createTextNode(' ' + enzyme.enzyme_name + ' cut'));
        $legend.append($item);
    });

});
