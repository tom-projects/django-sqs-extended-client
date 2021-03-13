from django.conf import settings

from ..aws.sns_client_extended import SNSClientExtended
from .event_base import EventBase


class EventBaseAws(EventBase):

    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION
    AWS_S3_QUEUE_STORAGE_NAME = settings.AWS_S3_QUEUE_STORAGE_NAME
    AWS_SNS_TOPIC = settings.AWS_SNS_TOPIC

    def dispatch(self, event_name, event_data):
        sns = SNSClientExtended(self.AWS_ACCESS_KEY_ID,
                                self.AWS_SECRET_ACCESS_KEY,
                                self.AWS_DEFAULT_REGION,
                                self.AWS_S3_QUEUE_STORAGE_NAME)
        return sns.send_message(
            self.AWS_SNS_TOPIC,
            event_data,
            message_attributes={
                'event_type': {
                    'DataType': 'String',
                    'StringValue': event_name
                }
            }
        )
