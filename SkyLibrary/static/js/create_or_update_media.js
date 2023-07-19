$(document).ready(function () {

    let form = $('#form');

    let file_input = form.find('#id_file');

    file_input.before(`<section class="file-status mb-1">${waiting_text_translated}</section>`);

    let file_key_input = form.find('#id_file_key');

    file_key_input.val(undefined);

    $(document).on('change', '#id_file', function () {

        let submit_button = form.find('button[type="submit"]');
        let status = form.find('.file-status');

        if ($(this).prop('files').length === 0) {

            status.text(waiting_text_translated);

            file_input.val('');
            file_key_input.val('');

            return;
        }

        let file = $(this).prop('files')[0];

        let filename = file.name;

        $.ajax('/en-us/media/create_or_update/s3auth/?' + 'file_name=' + filename).done(function (data) {

            let form_data = new FormData();

            for (let key in data.form_args.fields) {
                if (data.form_args.fields.hasOwnProperty(key)) {
                    form_data.append(key, data.form_args.fields[key]);
                }
            }

            form_data.append('file', file);

            status.text(uploading_text_translated);

            file_input.prop('disabled', true);
            submit_button.prop('disabled', true);

            $.ajax({
                method: 'POST',
                url: data.form_args.url,
                data: form_data,
                processData: false,
                contentType: false,
                success: function() {

                    status.text(uploaded_text_translated);

                    file_key_input.val(this.data.get('key'));
                },
                error: function() {

                    status.text(error_text_translated);

                    file_input.val('');
                    file_key_input.val('');
                },
                complete: function () {

                    file_input.prop('disabled', false);
                    submit_button.prop('disabled', false);
                }
            });
        });
    });

    $(document).on('submit', '#form', function () {

        if (file_key_input.val() !== '' && file_key_input.val() !== undefined) {
            form.find('#file-clear_id').prop('checked', true);
        }

        file_input.val('');
    });
});
