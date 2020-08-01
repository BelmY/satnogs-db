// This script handles adjustments in the user interface of the transmitter
// modals (like changing between Transmitter, Transceiver, and Transponder)
//
// NOTE: Since this script is loaded dynamically after page load, we have
// to be cautious of CSP requirements. Any changes to this script will need
// to have the hash recalculated and changed in settings.py under
// CSP_SCRIPT_SRC

function transmitter_suggestion_type(selection) {
    switch(selection){
    case 'Transmitter':
        $('.input-group').has('input[name=\'uplink_low\']').addClass('d-none');
        $('.input-group').has('input[name=\'uplink_high\']').addClass('d-none');
        $('.input-group').has('input[name=\'uplink_drift\']').addClass('d-none');
        $('.input-group').has('input[name=\'downlink_high\']').addClass('d-none');
        $('.input-group').has('input[name=\'invert\']').addClass('d-none');
        $('.input-group').has('select[name=\'uplink_mode\']').addClass('d-none');
        $('input[name=\'uplink_high\']').val('');
        $('input[name=\'downlink_high\']').val('');
        $('select[name=\'invert\']').removeAttr('checked');
        $('input[name=\'uplink_low\']').val('');
        $('input[name=\'uplink_drift\']').val('');
        $('select[name=\'uplink_mode\']').val('');
        $('.input-group-prepend:contains(\'Downlink Low\')').html('Downlink');
        break;
    case 'Transceiver':
        $('.input-group').has('input[name=\'uplink_high\']').addClass('d-none');
        $('.input-group').has('input[name=\'downlink_high\']').addClass('d-none');
        $('.input-group').has('input[name=\'invert\']').addClass('d-none');
        $('.input-group').has('input[name=\'uplink_low\']').removeClass('d-none');
        $('.input-group').has('input[name=\'uplink_drift\']').removeClass('d-none');
        $('.input-group').has('select[name=\'uplink_mode\']').removeClass('d-none');
        $('input[name=\'uplink_high\']').val('');
        $('input[name=\'downlink_high\']').val('');
        $('select[name=\'invert\']').removeAttr('checked');
        $('input[name=\'downlink_low\']').prev().html('Downlink');
        $('input[name=\'uplink_low\']').prev().html('Uplink');
        break;
    case 'Transponder':
        $('.input-group').has('input[name=\'uplink_high\']').removeClass('d-none');
        $('.input-group').has('input[name=\'downlink_high\']').removeClass('d-none');
        $('.input-group').has('input[name=\'invert\']').removeClass('d-none');
        $('.input-group').has('input[name=\'uplink_low\']').removeClass('d-none');
        $('.input-group').has('input[name=\'uplink_drift\']').removeClass('d-none');
        $('.input-group').has('select[name=\'uplink_mode\']').removeClass('d-none');
        $('input[name=\'downlink_low\']').prev().html('Downlink low');
        $('input[name=\'uplink_low\']').prev().html('Uplink low');
        break;
    }
}

$(function () {
    transmitter_suggestion_type($('#id_type option:selected').text());

    $('#id_type').on('change click', function () {
        var selection = $(this).val();
        transmitter_suggestion_type(selection);
    });
});