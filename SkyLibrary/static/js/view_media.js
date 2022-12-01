$('#download_link').click(function () {
    $.ajax({
        url: get_full_path,
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'request_type': 'download_file',
        },
        success: function (response) {

            $('#downloads_number').text(response.downloads_number);

            $('#download_link').addClass('btn-success');
            $('#download_link').removeClass('btn-primary');
        }
    });
});
