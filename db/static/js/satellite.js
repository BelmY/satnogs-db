/* eslint new-cap: "off" */
function copyToClipboard(text, el) {
    var copyTest = document.queryCommandSupported('copy');
    var elOriginalText = el.attr('data-original-title');

    if (copyTest === true) {
        var copyTextArea = document.createElement('textarea');
        copyTextArea.value = text;
        document.body.appendChild(copyTextArea);
        copyTextArea.select();
        try {
            var successful = document.execCommand('copy');
            var msg = successful ? 'Copied!' : 'Whoops, not copied!';
            el.attr('data-original-title', msg).tooltip('show');
        } catch (err) {
            window.alert('Oops, unable to copy');
        }
        document.body.removeChild(copyTextArea);
        el.attr('data-original-title', elOriginalText);
    } else {
        // Fallback if browser doesn't support .execCommand('copy')
        window.prompt('Copy to clipboard: Ctrl+C or Command+C, Enter', text);
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

function format_freq(freq) {
    var frequency = +freq; 
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
    // Calculate the drifted frequencies
    $('.drifted').each(function() {
        var drifted = ppb_to_freq($(this).data('freq_or'),$(this).data('drift'));
        $(this).html(drifted);
    });

    $('.uplink-drifted-sugedit').on('change click', function(){
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('input[name=\'uplink_low\']:visible').val());
        $('.uplink-ppb-sugedit').val(freq_to_ppb(freq_obs,freq));
    });

    $('.downlink-drifted-sugedit').on('change click', function(){
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('input[name=\'downlink_low\']:visible').val());
        $('.downlink-ppb-sugedit').val(freq_to_ppb(freq_obs,freq));
    });

    // Format all frequencies
    $('.frequency').each(function() {
        var to_format = $(this).html();
        $(this).html(format_freq(to_format));
    });

    // Copy UUIDs
    $('.js-copy').click(function() {
        var text = $(this).attr('data-copy');
        var el = $(this);
        copyToClipboard(text, el);
    });

    // Update Satellite
    $('.bs-modal').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url')
        });
    });

    // Update Transmitter
    $('.update-transmitter-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#update-transmitter-modal'
        });
    });

    // New transmitter links
    $('.create-transmitter-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#create-transmitter-modal'
        });
    });

    // Ask for help in a toast if this Satellite object is flagged as in need
    if ($('#satellite_name').data('needshelp') == 'True') {
        $(document).Toasts('create', {
            title: 'Please Help!',
            class: 'alert-warning',
            autohide: true,
            delay: 6000,
            icon: 'fas fa-hand-holding-medical',
            body: 'This Satellite needs editing. <a href="https://wiki.satnogs.org/Get_In_Touch" target="_blank">Contact us</a> to become an editor.'
        });
    }
});
