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

                $('#download_link').addClass('btn-success');
                $('#download_link').removeClass('btn-primary');
            },
        });
    });

    function getCommentHTML (comment, comment_nesting) {

        /* start comment */
        let new_comment = `<section id="comment_${comment.id}" data-comment-nesting="${comment_nesting}">`;

        /* start nesting */
        for (let i = 0; i < comment_nesting; i++) {
            new_comment += '<div class="ms-4">'
        }

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
        new_comment += `<button class="reply-button bg-transparent border-0 p-0 fw-light ms-2 mt-1" data-reply-button-target-id="${comment.id}">`;
        new_comment += `${comment.reply_translate}`;
        new_comment += '</button>';

        /* dot part */
        new_comment += '<span class="dot ms-2 mt-1"></span>';

        /* add url fragment link */
        new_comment += `<a href="#comment_${comment.id}" class="ms-2 mt-1">`;
        new_comment += '<ion-icon name="pin-outline" style="font-size: 14px;"></ion-icon>';
        new_comment += '</a>';

        /* close bottom line */
        new_comment += '</section>';

        /* add the section for reply form and messages */
        new_comment += `<section class="m-3" data-reply-target-id="${comment.id}"></section>`;

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

    $(document).on('click', '.reply-button', function () {
        $.ajax({
            url: get_full_path,
            type: 'GET',
            dataType: 'json',
            triggeredButton: this,
            data: {
                'request_type': 'get_comment_reply_form',
            },
            success: function (response) {

                let create_comment_reply_form_element = $('#create_comment_reply_form');
                let create_comment_reply_form_messages_element = $('#create_comment_reply_form_messages');

                if (create_comment_reply_form_element.html()) {

                    create_comment_reply_form_element.remove();
                    create_comment_reply_form_messages_element.remove();
                }

                let messages_ul = '<ul class="mt-2 text-danger" id="create_comment_reply_form_messages"></ul>'

                let target_id = $(this.triggeredButton).attr('data-reply-button-target-id');

                let reply_section_tag = $(`section[data-reply-target-id="${target_id}"]`);

                reply_section_tag.html(reply_section_tag.html() + messages_ul + response.comment_reply_form);
            },
        });
    });

    $(document).on('submit', '#create_comment_reply_form', function () {
        $.ajax({
            url: get_full_path,
            type: 'POST',
            dataType: 'json',
            targetNesting: parseInt($(this).parent().parent().attr('data-comment-nesting')),
            targetId: $(this).parent().attr('data-reply-target-id'),
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'request_type': 'create_comment',
                'target_type': 'comment',
                'target_id': $(this).parent().attr('data-reply-target-id'),
                'content': $('#add_comment_reply_content_field').val(),
            },
            success: function (response) {

                if (response.comment) {

                    let target_comment_position = $(`#comments section[id="comment_${this.targetId}"]`);

                    for (let i = 0; i < this.targetNesting; i++) {
                        target_comment_position = target_comment_position.parent();
                    }

                    target_comment_position.after(getCommentHTML(response.comment, this.targetNesting + 1));
                }

                let reply_messages_tag = $('#create_comment_reply_form_messages');

                reply_messages_tag.text('');

                if (response.messages) {

                    let messages = '';

                    for (let message of response.messages) {
                        messages += `<li class="${message.tags}">${message.message}</li>`;
                    }

                    reply_messages_tag.html(`${reply_messages_tag.html()}${messages}`);
                }
            },
            error: function (response) {

                let reply_messages_tag = $('#create_comment_reply_form_messages');

                reply_messages_tag.text('');

                let messages = '';

                for (let message of response.messages) {
                    messages += `<li class="${message.tags}">${message.message}</li>`;
                }

                reply_messages_tag.html(`${reply_messages_tag.html()}${messages}`);
            },
        });
        return false;
    });
});
