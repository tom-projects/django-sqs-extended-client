import json

from django.conf import settings


def process_event(event_message):

    content = event_message.get('Body').get('Message')

    if 'content_type' in event_message.get('Body').get('MessageAttributes'):
        content_type = event_message.get('Body').get('MessageAttributes').get('content_type')
        if content_type == 'json':
            data = json.loads(content)
        else:
            data = content
    else:
        data = content

    event_type = event_message.get('Body').get('MessageAttributes').get('event_type')

    try:
        event_processor_class_path = settings.SQS_EVENTS[event_type]['event_processor']
    except KeyError as e:
        raise NotImplementedError(f'event_processor not implemented for settings.SQS_EVENTS[{event_type}]')

    event_processor_class = globals()[event_processor_class_path]
    event_processor_class(data=data).execute()
