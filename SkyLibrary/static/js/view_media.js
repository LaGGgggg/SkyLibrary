$(document).ready(function() {

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

                let download_link_element = $('#download_link');

                download_link_element.addClass('btn-success');
                download_link_element.removeClass('btn-primary');
            },
        });
    });

    function getCommentHTML (comment, comment_nesting) {

        /* start comment */
        let new_comment = '';

        /* start nesting */
        for (let i = 0; i < comment_nesting; i++) {
            new_comment += '<div class="ms-4">'
        }

        new_comment += `<section id="comment_${comment.id}" data-comment-nesting="${comment_nesting}">`;

        /* top line */
        new_comment += '<section class="mt-4 small fst-italic">';

        new_comment += `<span class="fw-bold me-1">${comment.user_who_added}</span>`;
        new_comment += '<span class="dot"></span>';
        new_comment += `<span class="fw-light ms-1">${comment.pub_date}</span>`;

        new_comment += '</section>';

        /* content line */
        new_comment += `<section class="fs-5 mt-1">${comment.content}</section>`

        /* bottom line */
        new_comment += '<section class="d-flex flex-row align-items-center">';

        /* votes part */
        new_comment += '<section class="d-flex flex-column">';

        new_comment += `<button class="bg-transparent border-0 p-0 vote-button" data-vote-button-type="upvote" data-vote-button-target-id="${comment.id}">`;
        new_comment += '<ion-icon name="caret-up-outline"></ion-icon>';
        new_comment += '</button>';

        new_comment += `<button class="bg-transparent border-0 p-0 vote-button" data-vote-button-type="downvote" data-vote-button-target-id="${comment.id}">`;
        new_comment += '<ion-icon name="caret-down-outline"></ion-icon>';
        new_comment += '</button>';

        new_comment += '</section>';

        /* rating part */
        new_comment += `<section class="ms-2 mt-1" data-vote-rating-section-target-id="${comment.id}">0</section>`;

        /* dot part */
        new_comment += '<span class="dot ms-2 mt-1"></span>';

        /* add reply part */
        new_comment += `<button class="reply-button bg-transparent border-0 p-0 fw-light ms-2 mt-1" data-form-adder-button-target-id="${comment.id}" data-requested-form-type="reply">`;
        new_comment += `${comment.reply_translate}`;
        new_comment += '</button>';

        /* dot part */
        new_comment += '<span class="dot ms-2 mt-1"></span>';

        /* add report part */
        new_comment += `<button class="bg-transparent border-0 p-0 ms-2 mt-2 report-button" data-form-adder-button-target-id="${comment.id}" data-requested-form-type="report">`;
        new_comment += '<ion-icon name="alert-circle-outline"></ion-icon>';
        new_comment += '</button>';

        /* add uri fragment link */
        new_comment += `<a href="#comment_${comment.id}" class="ms-1 mt-2">`;
        new_comment += '<ion-icon name="pin-outline"></ion-icon>';
        new_comment += '</a>';

        /* close bottom line */
        new_comment += '</section>';

        /* add the section for reply or report form and messages */
        new_comment += `<section class="m-3" data-section-for-form-under-comment-target-id="${comment.id}"></section>`;

        /* close comment */
        new_comment += '</section>';

        /* close nesting */
        for (let i = 0; i < comment_nesting; i++) {
            new_comment += '</div>'
        }

        return new_comment;
    }

    $('#create_media_comment_form').submit(function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'create_comment',
                'target_type': 'media',
                'content': $('#add_media_comment_content_field').val(),
            },
            success: function (response) {

                if (response.comment) {
                    $('#comments').html(getCommentHTML(response.comment, 0) + $('#comments').html());
                }

                $('#messages').text('');

                if (response.messages) {

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `<li class="${message.tags}">${message.message}</li>`;
                    }

                    $('#add_comment_messages').html(messages);
                }
            },
            error: function (response) {

                $('#messages').text('');

                let messages = '';

                for (let message of response.messages) {
                    messages += `<li class="${message.tags}">${message.message}</li>`;
                }

                $('#add_comment_messages').html(messages);
            },
        });
        return false;
    });

    $(document).on('click', '.vote-button', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            triggeredButton: this,
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'add_comment_vote',
                'vote_type': $(this).attr('data-vote-button-type'),
                'target_id': $(this).attr('data-vote-button-target-id'),
            },
            success: function (response) {

                if (response.messages) {

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `${message.message}\n`;
                    }

                    alert(messages);

                } else {

                    $(`*[data-vote-rating-section-target-id="${response.target_id}"]`).text(response.new_rating);

                    let not_triggerd_button = $(`*[data-vote-button-type="${response.not_target_type}"][data-vote-button-target-id="${response.target_id}"]`);

                    if (this.triggeredButton.getAttribute('class').includes('vote-button-active')) {
                        $(this.triggeredButton).removeClass('vote-button-active');

                    } else {

                        $(this.triggeredButton).addClass('vote-button-active');

                        not_triggerd_button.removeClass('vote-button-active');
                    }
                }
            },
        });
    });

    function removeUnderCommentAndMediaFormsAndMessages () {

        let under_comment_form_element = $('#under_comment_form');

        if (under_comment_form_element.html()) {

            under_comment_form_element.remove();
            $('#under_comment_form_messages').remove();
        }

        let media_report_form_element = $('#media_report_form');

        if (media_report_form_element.html()) {

            media_report_form_element.remove();
            $('#media_report_form_messages').remove();
        }
    }

    $(document).on('click', '.reply-button, .report-button', function () {
        $.ajax({
            url: get_full_path,
            type: 'GET',
            dataType: 'json',
            triggeredButton: this,
            data: {
                'request_type': `get_comment_${$(this).attr('data-requested-form-type')}_form`,
            },
            success: function (response) {

                removeUnderCommentAndMediaFormsAndMessages();

                let messages_ul = '<ul class="mt-2 text-danger" id="under_comment_form_messages"></ul>';

                let target_id = $(this.triggeredButton).attr('data-form-adder-button-target-id');

                let section_for_form_under_comment_tag = $(`section[data-section-for-form-under-comment-target-id="${target_id}"]`);

                section_for_form_under_comment_tag.html(messages_ul + response.under_comment_form);
            },
        });
    });

    $(document).on('click', '.media-report-button', function () {
       $.ajax({
           url: get_full_path,
           type: 'GET',
           dataType: 'json',
           data: {
               'request_type': 'get_media_report_form',
           },
           success: function (response) {

               removeUnderCommentAndMediaFormsAndMessages();

               let messages_ul = '<ul class="mt-2 text-danger" id="media_report_form_messages"></ul>'

               let section_for_media_report_form_tag = $('#section_for_media_report_form');

               section_for_media_report_form_tag.html(messages_ul + response.media_report_form);
           },
       });
    });

    $(document).on('submit', '#under_comment_form', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            targetNesting: parseInt($(this).parent().parent().attr('data-comment-nesting')),
            targetId: $(this).parent().attr('data-section-for-form-under-comment-target-id'),
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': $(this).attr('data-request-type'),
                'target_type': 'comment',
                'target_id': $(this).parent().attr('data-section-for-form-under-comment-target-id'),
                'content': $('#under_comment_form_content_field').val(),
                'report_type': `${$.map($('[name="report_type"]'), function (element) {
                    if (element.checked) {
                        return element.value;
                    }
                })}`,  // into a string for the correct operation of the backend
            },
            success: function (response) {

                if (response.comment) {

                    let target_comment_position = $(`#comments section[id="comment_${this.targetId}"]`);

                    for (let i = 0; i < this.targetNesting; i++) {
                        target_comment_position = target_comment_position.parent();
                    }

                    target_comment_position.after(getCommentHTML(response.comment, this.targetNesting + 1));

                } else if (response.report_success_message) {

                    removeUnderCommentAndMediaFormsAndMessages();

                    alert(response.report_success_message);

                } else {

                    let under_comment_form_messages_tag = $('#under_comment_form_messages');

                    under_comment_form_messages_tag.text('');

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `<li class="${message.tags}">${message.message}</li>`;
                    }

                    under_comment_form_messages_tag.html(`${under_comment_form_messages_tag.html()}${messages}`);
                }
            },
            error: function (response) {

                let under_comment_form_messages_tag = $('#under_comment_form_messages');

                under_comment_form_messages_tag.text('');

                let messages = '';

                for (let message of response.messages) {
                    messages += `<li class="${message.tags}">${message.message}</li>`;
                }

                under_comment_form_messages_tag.html(`${under_comment_form_messages_tag.html()}${messages}`);
            },
        });
        return false;
    });

    $(document).on('submit', '#media_report_form', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'create_report',
                'target_type': 'media',
                'content': $('#media_report_form_content_field').val(),
                'report_type': `${$.map($('[name="report_type"]'), function (element) {
                    if (element.checked) {
                        return element.value;
                    }
                })}`,  // into a string for the correct operation of the backend
            },
            success: function (response) {

                if (response.report_success_message) {

                    removeUnderCommentAndMediaFormsAndMessages();

                    alert(response.report_success_message);

                } else {

                    let media_report_form_messages_tag = $('#media_report_form_messages');

                    media_report_form_messages_tag.text('');

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `<li class="${message.tags}">${message.message}</li>`;
                    }

                    media_report_form_messages_tag.html(`${media_report_form_messages_tag.html()}${messages}`);
                }
            },
            error: function (response) {

                let media_report_form_messages_tag = $('#media_report_form_messages');

                media_report_form_messages_tag.text('');

                let messages = '';

                for (let message of response.messages) {
                    messages += `<li class="${message.tags}">${message.message}</li>`;
                }

                media_report_form_messages_tag.html(`${media_report_form_messages_tag.html()}${messages}`);
            },
        });
        return false;
    });
});
