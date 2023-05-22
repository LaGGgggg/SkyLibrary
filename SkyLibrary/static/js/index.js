$(document).ready(function() {

    $(document).on('click', '#get_search_media_form_button', function () {
        $.ajax({
            url: get_full_path,
            type: 'GET',
            dataType: 'json',
            data: {
                'request_type': 'get_search_media_form',
            },
            success: function (response) {

                let messages_ul = '<ul class="mt-2 text-danger" id="search_media_form_messages"></ul>';

                let section_for_search_media_form_tag = $('#section_for_search_media_form');
                section_for_search_media_form_tag.addClass('border border-info mb-2');

                let section_for_search_results = '<section id="section_for_search_results" class="m-2"></section>';

                section_for_search_media_form_tag.html(
                    messages_ul + response.search_media_form + section_for_search_results
                );
            },
        });
    });

    $(document).on('submit', '#search_media_form', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'search_media',
                'text': $('#search_media_form_text_field').val(),
                'tags': `${$.map($('[name="tags"]'), function (element) {
                    if (element.checked) {
                        return element.value;
                    }
                })}`  // into a string for the correct operation of the backend
            },
            success: function (response) {

                if (response.search_results) {

                    let search_results_html = '';

                    for (const [title, data] of Object.entries(response.search_results)) {

                        search_results_html += '<section class="mt-2">';

                        // open flex-row section
                        search_results_html += '<section class="list-group flex-row align-items-center">';

                        // link part

                        search_results_html += '<section class="fs-4">';

                        search_results_html += `<a href="${data.link}">${title}</a>`;

                        search_results_html += '</section>';

                        // rating part

                        search_results_html += '<section class="d-inline-flex align-items-end rating ms-1" style="font-size: 80%">';

                        search_results_html += '<section class="position-relative rating__stars_body">';

                        search_results_html += '<section class="position-absolute rating__stars"></section>';

                        search_results_html += '</section>';

                        search_results_html += '<section class="rating__value">';

                        search_results_html += data.rating;

                        search_results_html += '</section>';

                        search_results_html += '</section>';

                        // close flex-rpw section
                        search_results_html += '</section>';

                        // tags part
                        search_results_html += '<section class="small fw-light">';

                        for (const tag of data.tags) {
                            search_results_html += `<a data-toggle="tooltip" title="${tag.help_text}" href="">#${tag.name}</a>  `;
                        }

                        search_results_html += '</section>';

                        search_results_html += '</section>';
                    }

                    $('#section_for_search_results').html(search_results_html);

                    updateRatings();
                }

                $('#search_media_form_messages').text('');

                if (response.messages) {

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `<li class="${message.tags}">${message.message}</li>`;
                    }

                    $('#search_media_form_messages').html(messages);
                }
            },
            error: function (response) {

                $('#search_media_form_messages').text('');

                let messages = '';

                for (let message of response.messages) {
                    messages += `<li class="${message.tags}">${message.message}</li>`;
                }

                $('#search_media_form_messages').html(messages);
            },
        });
        return false;
    });
});