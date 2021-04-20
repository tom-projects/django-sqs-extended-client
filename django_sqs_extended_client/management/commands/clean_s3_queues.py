import datetime

import boto3
import pytz
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-kd',
            '--keep_days',
            type=int,
            default=3
        )

    def handle(self, *args, **options):
        keep_days = options['keep_days']

        from_date = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - datetime.timedelta(days=keep_days)

        s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        files = s3_client.list_objects_v2(Bucket=settings.AWS_S3_QUEUE_STORAGE_NAME)['Contents']

        keys_to_delete = [
            {'Key': bucket_item['Key']} for bucket_item in files
            if bucket_item['LastModified'] < from_date
        ]

        print('Keys to delete')
        print(len(keys_to_delete))
        print(keys_to_delete)
        response = s3_client.delete_objects(Bucket=settings.AWS_S3_QUEUE_STORAGE_NAME,
                                            Delete={'Objects': keys_to_delete})
        print(response)
