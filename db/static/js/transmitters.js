function ppb_to_freq(freq, drift) {
    var freq_obs = freq + ((freq * drift) / Math.pow(10,9));
    return Math.round(freq_obs);
}

/* eslint-disable no-unused-vars */
/* Disabling eslint for the following function since it is called by the Bootstrap Table library */
function freqSorter(a, b) {
    var aa = a.split(' ', 1);
    var bb = b.split(' ', 1);
    return aa - bb;
}
/* eslint-enable no-unused-vars */

$(document).ready(function() {

    $('#transmitters-table').bootstrapTable();
    $('#transmitters-table').css('opacity','1');

    // Calculate the drifted frequencies
    $('.drifted').each(function() {
        var drifted = ppb_to_freq($(this).data('freq_or'),$(this).data('drift'));
        $(this).html(drifted);
    });
});
