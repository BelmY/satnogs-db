function ppb_to_freq(freq, drift) {
    var freq_obs = freq + ((freq * drift) / Math.pow(10,9));
    return Math.round(freq_obs);
}

function format_freq(frequency) {
    if (isNaN(frequency) || frequency == ''){
        return 'None';
    } else if (frequency < 1000) {
    // Frequency is in Hz range
        return frequency.toFixed(3) + ' Hz';
    } else if (frequency < 1000000) {
        return (frequency/1000).toFixed(3) + ' kHz';
    } else {
        return (frequency/1000000).toFixed(3) + ' MHz';
    }
}

$(document).ready(function() {

    $('#transmitters-table').bootstrapTable();
    $('#transmitters-table').css('opacity','1');

    $( '#transmitters-table' ).on('pre-body.bs.table', function() {
        $('.frequency').each(function() {
            var to_format = $(this).html();
            $(this).html(format_freq(to_format));
        });
    });

    // Calculate the drifted frequencies
    $('.drifted').each(function() {
        var drifted = ppb_to_freq($(this).data('freq_or'),$(this).data('drift'));
        $(this).html(drifted);
    });
});
