$(document).ready(function() {
    $('#receive_task_button').click(function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf_token,
            },
            success: function (response) {

                $('#receive_task_button').remove();

                if (response.moderator_task === null) {
                    $('#moderator_task_link_no_available').css('display', 'block');
                }
                else {
                    $('#moderator_task_link').wrapInner(`${response.moderator_task}`);
                }
            }
        });
    });
});
