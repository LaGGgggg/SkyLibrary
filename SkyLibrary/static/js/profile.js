$(document).ready(function() {

    $(document).on('mousemove', '.dynamic-rating', function (e) {

        let x = Math.round(e.clientX - $(this).offset().left);

        let width = $(this).width();

        $(this).find('.rating__stars').css('width', `${x / width * 100}%`);
    });

    $(document).on('click', '.dynamic-rating', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            triggeredElement: this,
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'update_media_rating',
                'media_id': `${$(this).parent().find('.rating__value').attr('data-media-id')}`,
                'new_rating': `${Math.round(parseInt($(this).find('.rating__stars')[0].style.width.replace('%', '')) / 20) || 1}`,
            },
            success: function (response) {
                if (response.result_rating) {

                    $(this.triggeredElement).parent().find('.rating__value').text(response.result_rating);

                    updateRatings();
                }
            },
        });
    });
});
