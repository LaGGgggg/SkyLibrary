$(document).ready(async function () {

    let form = $('#form');

    let file_input = form.find('#id_file');

    file_input.before(`<section class="d-inline file-status">${waiting_text_translated}</section>`);
    file_input.before(`<section id="file-status-percents" class="d-inline ms-2"></section>`);

    let file_key_input = form.find('#id_file_key');

    file_key_input.val(undefined);

    await $(document).on('change', '#id_file', async function () {

        let submit_button = form.find('button[type="submit"]');
        let status = form.find('.file-status');
        let status_percents = form.find('#file-status-percents');

        if ($(this).prop('files').length === 0) {

            status.text(waiting_text_translated);

            file_input.val('');
            file_key_input.val('');

            return;
        }

        let file = $(this).prop('files')[0];

        await $.ajax(`/en-us/media/create_or_update/s3auth/get_data_for_upload/${file.name}/`).done(async function (multipart_upload_data) {

            const upload_id = multipart_upload_data.upload_id;
            const file_key = multipart_upload_data.file_key;
            const chunk_size = multipart_upload_data.chunk_size;

            const status_percents_step = Math.ceil(100 / (file.size / chunk_size));

            let chunk_number = 0;

            let chunk_start = -chunk_size;
            let chunk_end = 0;

            let chunks_numbers_with_etags = [];

            let current_status_percents_value = 0;

            status.text(uploading_text_translated);
            status_percents.text(`${current_status_percents_value}%`);

            file_input.prop('disabled', true);
            submit_button.prop('disabled', true);

            function upload_parts() {

                chunk_start += chunk_size;

                chunk_end = Math.min(chunk_end + chunk_size, file.size);

                chunk_number++;

                const chunk = file.slice(chunk_start, chunk_end);

                let is_break = false;
                let is_complete_successful = true;

                $.ajax(`/en-us/media/create_or_update/s3auth/get_upload_part_presigned_url/${upload_id}/${chunk_number}/${file_key}/`).done(function (upload_url) {
                    $.when($.ajax({
                        method: 'PUT',
                        url: upload_url.upload_url,
                        data: chunk,
                        processData: false,
                        contentType: false,
                        cache: false,
                        success: function (data, textStatus, jqXHR) {

                            current_status_percents_value += status_percents_step;

                            if (current_status_percents_value >= 100) {
                                current_status_percents_value = 99;
                            }

                            status_percents.text(`${current_status_percents_value}%`);

                            chunks_numbers_with_etags.push(
                                {'PartNumber': chunk_number, 'ETag': jqXHR.getResponseHeader('Etag').replace(new RegExp('"', 'g'), '')}
                            );
                        },
                        error: function () {
                            is_break = true;
                            is_complete_successful = false;
                        },
                    })).done(function () {

                        if (!is_break && (chunk_start + chunk_size >= file.size)) {

                            file_input.prop('disabled', false);
                            submit_button.prop('disabled', false);

                            status_percents.text('100%');

                            if (is_complete_successful) {

                                status.text(uploaded_text_translated);

                                file_key_input.val(file_key);

                                $.ajax({
                                    method: 'POST',
                                    url: `/en-us/media/create_or_update/s3auth/do_complete/${upload_id}/${file_key}/`,
                                    dataType: 'json',
                                    data: {
                                        'csrfmiddlewaretoken': csrf_token,
                                        'upload_parts': JSON.stringify(chunks_numbers_with_etags),
                                    },
                                });
                            } else {

                                status.text(error_text_translated);

                                file_input.val('');
                                file_key_input.val('');

                                $.ajax({
                                    method: 'POST',
                                    url: `/en-us/media/create_or_update/s3auth/do_abort/${upload_id}/${file_key}/`,
                                    dataType: 'json',
                                    data: {
                                        'csrfmiddlewaretoken': csrf_token,
                                    },
                                });
                            }
                        } else {
                            upload_parts();
                        }
                    });
                });
            }

            upload_parts();
        });
    });

    $(document).on('submit', '#form', function () {

        if (file_key_input.val() !== '' && file_key_input.val() !== undefined) {
            form.find('#file-clear_id').prop('checked', true);
        }

        file_input.val('');
    });
});
