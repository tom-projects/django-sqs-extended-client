from django.conf import settings
from django.core.management.base import BaseCommand
from django_sqs_extended_client.aws.sns_client_extended import SNSClientExtended
from django_sqs_extended_client.queue.common import SignalHandler
import pydoc
import json


class Command(BaseCommand):
    help = 'Process Queue'

    def add_arguments(self, parser):
        parser.add_argument(
            'queue_code',
            type=str,
        )

    def handle(self, *args, **options):
        queue_code = options['queue_code']

        try:
            sqs_event = settings.SQS_EVENTS[queue_code]
        except KeyError:
            raise NotImplementedError(f'{queue_code} not implemented in settings.SQS_EVENTS')

        try:
            queue_url = sqs_event['sqs_queue_url']
        except KeyError:
            raise NotImplementedError(f"sqs_queue_url not implemented for settings.SQS_EVENTS[{queue_code}]")

        signal_handler = SignalHandler()

        while not self.get_received_signal(signal_handler=signal_handler):
            sns = SNSClientExtended(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                    settings.AWS_DEFAULT_REGION,
                                    settings.AWS_S3_QUEUE_STORAGE_NAME)
            messages = sns.receive_message(queue_url, 1, 10)
            if messages is not None and len(messages) > 0:
                for message in messages:
                    body = message.get('Body')
                    content = body.get('Message')
                    attributes = body.get('MessageAttributes')
                    self.process_event(content_data=content, attributes=attributes)
                    sns.delete_message(queue_url, message.get('ReceiptHandle'))

    @staticmethod
    def get_received_signal(signal_handler: SignalHandler):
        return signal_handler.received_signal

    @staticmethod
    def process_event(content_data, attributes):
        try:
            data = json.loads(content_data)
        except (json.JSONDecodeError, TypeError):
            data = content_data

        event_type = attributes.get('event_type')['Value']

        try:
            event_processor_class_path = settings.SQS_EVENTS[queue_code]['event_processor']
        except KeyError as e:
            raise NotImplementedError(f'event_processor not implemented for settings.SQS_EVENTS[{event_type}]')
        event_processor_class = pydoc.locate(event_processor_class_path)
        if event_processor_class is None:
            raise FileNotFoundError(f'File "{event_processor_class_path}" not found')
        event_processor_class(data=data).execute()
