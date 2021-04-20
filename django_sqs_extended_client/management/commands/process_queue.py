from time import sleep
from datetime import datetime
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

        parser.add_argument(
            '-s',
            '--default_sleep',
            type=float,
            default=0.2
        )

        parser.add_argument(
            '-e',
            '--exit_after_seconds',
            type=int,
            default=100
        )

        parser.add_argument(
            '-f',
            '--flush_s3',
            action='store_true',
        )

        parser.add_argument(
            '-m',
            '--max_number_of_messages',
            type=int,
            default=10,
            choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )

    def handle(self, *args, **options):
        start_dt = datetime.now()
        
        queue_code = options['queue_code']
        default_sleep = options['default_sleep']
        max_number_of_messages = options['max_number_of_messages']
        exit_after_seconds = options['exit_after_seconds']
        flush_s3 = options.get('flush_s3', False)
        
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
            now = datetime.now()
            seconds_after_start = (now - start_dt).seconds
            if seconds_after_start > exit_after_seconds:
                print(f'Exiting after {exit_after_seconds} seconds.')
                return

            sleep_time = default_sleep
            sns = SNSClientExtended(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                    settings.AWS_DEFAULT_REGION,
                                    settings.AWS_S3_QUEUE_STORAGE_NAME)
            messages = sns.receive_message(queue_url,
                                           max_number_of_messages=max_number_of_messages,
                                           wait_time_seconds=10)
            if messages is not None and len(messages) > 0:
                sleep_time = 0.001
                for message in messages:
                    body = message.get('Body')
                    content = body.get('Message')
                    attributes = body.get('MessageAttributes')
                    self.process_event(queue_code=queue_code, content_data=content, attributes=attributes)
                    sns.delete_message(queue_url=queue_url, receipt_handle=message.get('ReceiptHandle'),
                                       flush_s3=flush_s3)
            sleep(sleep_time)

    @staticmethod
    def get_received_signal(signal_handler: SignalHandler):
        return signal_handler.received_signal

    @staticmethod
    def process_event(queue_code, content_data, attributes):
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
        event_processor_class(data=data, attributes=attributes, queue_code=queue_code).execute()
