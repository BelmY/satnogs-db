/* eslint new-cap: "off" */
$(document).ready(function() {
    'use strict';

    // Add current copyright year
    var current_year = '-' + new Date().getFullYear();
    $('#copy').text(current_year);

    // Enable tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // User Settings / API Modal Form Link
    $('.basemodal-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#basemodal'
        });
        $(this).click(function() {
            $('#control-sidebar-toggle').ControlSidebar('toggle');
        });
    });

    // Transitional from inline alerts to Toasts
    $('.alert').each(function() {
        var alerticon = 'fas fa-question';
        var alerttitle = 'Unknown';
        if ($(this).data('alertclass') == 'alert-success') {
            alerticon = 'far fa-thumbs-up';
            alerttitle = 'Success';
        }
        if ($(this).data('alertclass') == 'alert-warning') {
            alerticon = 'fas fa-exclamation';
            alerttitle = 'Alert';
        }
        $(document).Toasts('create', {
            class: $(this).data('alertclass'),
            title: alerttitle,
            autohide: true,
            delay: 6000,
            icon: alerticon,
            body: $(this).data('alertmessage')
        });
    });
});
