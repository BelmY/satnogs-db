function suggestion_type(selection) {
    switch(selection){
    case 'Transmitter':
        $('.input-group').show();
        $('.input-group').has('input[name=\'uplink_low\']').hide();
        $('.input-group').has('input[name=\'uplink_high\']').hide();
        $('.input-group').has('input[name=\'uplink_drift\']').hide();
        $('.input-group').has('input[name=\'downlink_high\']').hide();
        $('.input-group').has('input[name=\'invert\']').hide();

        $('.input-group-addon:contains(\'Downlink Low\')').html('Downlink');
        break;
    case 'Transceiver':
        $('.input-group').show();
        $('.input-group').has('input[name=\'uplink_high\']').hide();
        $('.input-group').has('input[name=\'downlink_high\']').hide();
        $('.input-group').has('input[name=\'invert\']').hide();

        $('input[name=\'downlink_low\']').prev().html('Downlink');
        $('input[name=\'uplink_low\']').prev().html('Uplink');
        break;
    case 'Transponder':
        $('.input-group').show();
        $('input[name=\'downlink_low\']').prev().html('Downlink Low');
        $('input[name=\'uplink_low\']').prev().html('Uplink Low');
        break;
    }
}

function ppb_to_freq(freq, drift) {
    var freq_obs = freq + ((freq * drift) / Math.pow(10,9));
    return Math.round(freq_obs);
}

function freq_to_ppb(freq_obs, freq) {
    if(freq == 0){
        return 0;
    } else {
        return Math.round(((freq_obs / freq) - 1) * Math.pow(10,9));
    }
}

function format_freq(frequency) {
    if (frequency < 1000) {
    // Frequency is in Hz range
        return frequency.toFixed(3) + ' Hz';
    } else if (frequency < 1000000) {
        return (frequency/1000).toFixed(3) + ' kHz';
    } else {
        return (frequency/1000000).toFixed(3) + ' MHz';
    }
}

$(document).ready(function() {
    $('.suggestion-type').on('change click', function(){
        var selection = $(this).val();
        suggestion_type(selection);
    });

    $('.suggestion-edit-modal').on('show.bs.modal', function(){
        var selection =  $(this).find('.suggestion-type').val();
        suggestion_type(selection);

        var downlink_ppb = parseInt($(this).find('.downlink-ppb-sugedit').val());
        if(downlink_ppb){
            var freq_down = parseInt($(this).find('input[name=\'downlink_low\']').val());
            $('.downlink-drifted-sugedit').val(ppb_to_freq(freq_down,downlink_ppb));
        }

        var uplink_ppb = parseInt($(this).find('.uplink-ppb-sugedit').val());
        if(uplink_ppb){
            var freq_up = parseInt($(this).find('input[name=\'uplink_low\']').val());
            $('.uplink-drifted-sugedit').val(ppb_to_freq(freq_up,uplink_ppb));
        }
    });

    $('#NewSuggestionModal').on('show.bs.modal', function(){
        suggestion_type('Transmitter');
    });

    // Calculate the drifted frequencies
    $('.drifted').each(function() {
        var drifted = ppb_to_freq($(this).data('freq_or'),$(this).data('drift'));
        $(this).html(drifted);
    });

    $('.uplink-drifted-sugedit').on('change click', function(){
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('.in input[name=\'uplink_low\']').val());
        $('.uplink-ppb-sugedit').val(freq_to_ppb(freq_obs,freq));
    });

    $('.downlink-drifted-sugedit').on('change click', function(){
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('.in input[name=\'downlink_low\']').val());
        $('.downlink-ppb-sugedit').val(freq_to_ppb(freq_obs,freq));
    });

    // Format all frequencies
    $('.frequency').each(function() {
        var to_format = $(this).html();
        $(this).html(format_freq(to_format));
    });
});