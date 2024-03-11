import json
import boto3

from django.conf import settings
from django.core.management.base import BaseCommand
from library_collection.models import HarvestEvent, HarvestRun


def determine_run_status(run):
    '''Determine the status of a HarvestRun based on a Rikolti message
    '''
    most_recent_event = run.most_recent_event()
    rikolti_message = json.loads(most_recent_event.rikolti_message)

    if not isinstance(rikolti_message, dict):
        run.status = "running"
    else: 
        dag_complete = rikolti_message.get('dag_complete')
        if dag_complete:
            run.status = "succeeded"
        elif dag_complete is False:
            run.status = "failed"
        else:
            run.status = "running"

    run.save()
    return run


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
                sns_timestamp = sns_message['Timestamp']

                # TODO: Remove once we've processed all old messages sitting in
                # the queue
                if 'host' not in event_msg and 'version' not in event_msg:
                    event_msg['host'] = 'https://7a8067cb-3b99-477e-a883-7e311175a9b4.c3.us-west-2.airflow.amazonaws.com/'

                run = HarvestRun.objects.get_or_create_from_event(**event_msg)
                event_msg.update({
                    'harvest_run': run,
                    'sqs_message': sqs_message,
                    'sns_message': sns_message,
                    'sns_timestamp': sns_timestamp,
                })
                event = HarvestEvent.objects.create_from_event(**event_msg)
                determine_run_status(run)
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
        
