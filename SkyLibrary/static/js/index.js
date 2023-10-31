$(document).ready(function() {
    $(document).on('submit', '#filter_media_form', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'filter_media',
                'title': $('#filter_media_form_title_field').val(),
                'author': $('#filter_media_form_author_field').val(),
                'tags': `${$('#id_tags').val()}`,
                'rating_direction': $('#id_rating_direction').val(),
                'rating_minimum_value': $('#id_rating_minimum_value').val(),
                'rating_maximum_value': $('#id_rating_maximum_value').val(),
                'user_who_added': $('#filter_media_form_user_who_added_field').val(),
            },
            success: function (response) {
                if (response.filter_results && Object.keys(response.filter_results).length !== 0) {

                    let filter_results_html = '<hr>';

                    for (const media_data of response.filter_results) {

                        filter_results_html += '<section class="mt-2">';

                        // open flex-row section
                        filter_results_html += '<section class="list-group flex-row align-items-center">';

                        // link part

                        filter_results_html += '<section class="fs-4">';

                        filter_results_html += `<a href="${media_data.link}">${media_data.title}</a>`;

                        filter_results_html += '</section>';

                        // rating part

                        filter_results_html += '<section class="d-inline-flex align-items-end rating ms-1" style="font-size: 80%">';

                        filter_results_html += '<section class="position-relative rating__stars_body">';

                        filter_results_html += '<section class="position-absolute rating__stars"></section>';

                        filter_results_html += '</section>';

                        filter_results_html += '<section class="rating__value">';

                        filter_results_html += media_data.rating;

                        filter_results_html += '</section>';

                        filter_results_html += '</section>';

                        // close flex-rpw section
                        filter_results_html += '</section>';

                        // tags part
                        filter_results_html += '<section class="small fw-light">';

                        for (const tag of media_data.tags) {
                            filter_results_html += `<a data-toggle="tooltip" title="${tag.help_text}" href="">#${tag.name}</a>  `;
                        }

                        filter_results_html += '</section>';

                        filter_results_html += '</section>';

                        filter_results_html += '<hr>';
                    }

                    $('#section_for_filter_results').html(filter_results_html);

                    updateRatings();

                } else {
                    $('#section_for_filter_results').html(`<hr><section>${nothing_found_translated}</section>`);
                }
            },
        });
        return false;
    });
});
