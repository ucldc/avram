import json
import boto3

from django.conf import settings
from django.core.management.base import BaseCommand
from library_collection.models import HarvestEvent, HarvestRun


class Command(BaseCommand):
    help = 'Rikolti status'

    def process_events_from_sqs(self):
        sqs = boto3.client('sqs', **settings.AWS)

        queue_url=settings.RIKOLTI_EVENTS_QUEUE_URL
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,  # Enable long polling
        )
        if 'Messages' in messages:  # Check if any messages were received
            for sqs_message in messages['Messages']:
                sns_message = json.loads(sqs_message.pop('Body'))
                event_msg = json.loads(sns_message.pop('Message'))

                run = HarvestRun.objects.get_or_create_from_event(**event_msg)
                event_msg.update({
                    'harvest_run': run,
                })
                event = HarvestEvent.objects.create_from_event(**event_msg)
                # print(
                #     f"successfully created {run} and {event} from {event_msg}")

                # Delete processed message to prevent reprocessing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=sqs_message['ReceiptHandle']
                )
        else:
            print("No messages to process. Waiting for new messages...")


    def handle(self, *args, **options):
        self.process_events_from_sqs()
        
