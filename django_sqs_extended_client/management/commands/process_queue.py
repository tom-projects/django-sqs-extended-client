from django.conf import settings
from django.core.management.base import BaseCommand

from django_sqs_extended_client.aws.sns_client_extended import SNSClientExtended
from django_sqs_extended_client.queue.common import SignalHandler
from django_sqs_extended_client.process_event import process_event


class Command(BaseCommand):
    help = 'Process Queue'

    def add_arguments(self, parser):
        parser.add_argument(
            'queue_code',
            type=str,
        )

    def handle(self, *args, **options):
        queue_code = options['queue_code']

        signal_handler = SignalHandler()

        try:
            sns_event = getattr(settings.SNSEvent, 'queue_code')
        except AttributeError:
            raise NotImplementedError(f'{queue_code} not implemented in settings.SNSEvent')

        try:
            queue_url = settings.SQS_EVENTS[sns_event.value]['sqs_queue_url']
        except KeyError:
            raise NotImplementedError(f'sqs_queue_url not implemented for settings.SQS_EVENTS[{sns_event.name}.value]')

        while not signal_handler.received_signal:
            sns = SNSClientExtended(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_DEFAULT_REGION,
                                    settings.AWS_S3_QUEUE_STORAGE_NAME)
            messages = sns.receive_message(queue_url, 1, 10)
            if messages is not None and len(messages) > 0:
                for message in messages:
                    process_event(message)
                    sns.delete_message(queue_url, message.get('ReceiptHandle'))
