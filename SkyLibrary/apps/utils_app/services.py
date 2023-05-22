from django.contrib import messages

from json import dumps


def messages_to_json(request) -> str:
    result = []

    for message in messages.get_messages(request):
        result.append(
            {
                'level': message.level,
                'message': message.message[0] if isinstance(message.message, list) else message.message,
                'tags': message.tags,
            }
        )

    return dumps({'messages': result})
