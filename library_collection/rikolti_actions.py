import base64
import os
import re

from datetime import datetime

import boto3
import requests

from django.template.defaultfilters import pluralize
from django.utils.safestring import mark_safe
import django.contrib.messages as messages
from .models import HarvestTrigger
from collections import namedtuple

MwaaConnection = namedtuple('MWAA', ['token', 'hostname'])

def get_mwaa_cli_token():
    aws_access = {
        "aws_access_key_id": os.environ.get('AWS_ACCESS_KEY_ID'),
        "aws_secret_access_key": os.environ.get('AWS_SECRET_ACCESS_KEY'),
        "aws_session_token": os.environ.get('AWS_SESSION_TOKEN'),
        "region_name": 'us-west-2',
    }
    mwaa_client = boto3.client('mwaa', **aws_access)
    resp = mwaa_client.create_cli_token(Name="pad-airflow-mwaa")
    mwaa_token = resp.get('CliToken')
    mwaa_hostname = resp.get('WebServerHostname')
    return MwaaConnection(mwaa_token, mwaa_hostname)


def parse_cli_resp(resp):
    """Parse the response from the MWAA CLI"""
    # response is json object with keys: "stdout", "stderr"
    # values of stdout and stderr are base64 encoded strings

    cli_results = resp.json()
    stdout = base64.b64decode(cli_results.get('stdout')).decode('utf-8')
    stderr = base64.b64decode(cli_results.get('stderr')).decode('utf-8')

    return {'stdout': stdout, 'stderr': stderr}


def trigger_dag(mwaa, dag_id, collection_id):
    print(f"collection_id: {collection_id}")
    url = f"https://{mwaa.hostname}/aws_mwaa/cli"
    headers = {
        "Authorization": f"Bearer {mwaa.token}",
        "Content-Type": "text/plain",
    }
    data = (
        f"dags trigger -o yaml {dag_id} -c"
        f"'{{\"collection_id\": \"{collection_id}\"}}'"
    )
    resp = requests.post(url, headers=headers, data=data)
    return resp


def find_dag_run_id(stdout):
    dag_run_id = re.search(
        r"^\s*dag_run_id: (?P<dag_run_id>.+)$", 
        stdout, flags=re.MULTILINE
    )
    if dag_run_id:
        return dag_run_id.group('dag_run_id')


def find_logical_date(stdout):
    logical_date = re.search(
        r"^\s*logical_date:\s*'(?P<logical_date>.+)'$", 
        stdout, flags=re.MULTILINE
    )
    if logical_date:
        logical_date = datetime.strptime(
            logical_date.group('logical_date'), 
            "%Y-%m-%dT%H:%M:%S%z"
        )
        return logical_date


def trigger_harvest(collection, dag_id, mwaa):
    resp = trigger_dag(mwaa, dag_id, collection.id)
    if resp.status_code == 403:
        # maybe our token expired, get a new one and retry:
        mwaa = get_mwaa_cli_token()
        resp = trigger_dag(mwaa, dag_id, collection.id)
    resp.raise_for_status()

    parsed_resp = parse_cli_resp(resp)
    harvest_trigger = HarvestTrigger(
        collection=collection,
        dag_id=dag_id,
        hostname=mwaa.hostname,
        stdout=parsed_resp['stdout'],
        stderr=parsed_resp['stderr'],
        dag_run_id=find_dag_run_id(parsed_resp['stdout']),
        airflow_execution_time=find_logical_date(parsed_resp['stdout'])
    )
    harvest_trigger.save()

    return harvest_trigger


def create_success_message(harvest_trigger):
    return (
        f"✅ <a href='{harvest_trigger.collection.admin_url()}'>"
        f"{harvest_trigger.collection}</a> - Airflow Link: "
        f"<a href='{harvest_trigger.dag_run_link}'>"
        f"{harvest_trigger.dag_run_id}</a> - Log Output: "
        f"<a href='{harvest_trigger.admin_url()}'>Harvest Trigger</a>"
    )


def create_mwaa_failure_message(harvest_trigger):
    return (
        "⛔ There was a MWAA error trying to harvest "
        f"<a href='{harvest_trigger.collection.admin_url()}'>"
        f"{harvest_trigger.collection}</a> - check log output: "
        f"<a href='{harvest_trigger.admin_url()}'>harvest trigger</a>"
    )


def create_registry_failure_message(collection, e):
    return (
        "⛔ Something went wrong registry-side for collection "
        f"<a href='{collection.admin_url()}'>{collection}</a> - {str(e)}"
    )


def harvest_collection_set(modeladmin, request, queryset):
    """Harvest the selected collections"""
    mwaa = get_mwaa_cli_token()
    dag_id = 'validate_by_mapper_type'

    message = []
    success_count = 0
    notification_level = messages.SUCCESS
    for collection in queryset:
        try:
            harvest_trigger = trigger_harvest(collection, dag_id, mwaa)
            if harvest_trigger.stderr:
                message.append(
                    create_mwaa_failure_message(harvest_trigger))
                notification_level = messages.WARNING
            else:
                message.append(
                    create_success_message(harvest_trigger))
                success_count += 1
        except Exception as e:
            message.append(
                create_registry_failure_message(collection, e))
            notification_level = messages.WARNING

    if success_count == 0:
        notification_level = messages.ERROR

    msg = (
        f"Started {success_count} of {len(queryset)} "
        f"harvest{pluralize(success_count)}: <br/>" +
        '<br/>'.join(message)
    )

    modeladmin.message_user(request, mark_safe(msg), level=notification_level)

harvest_collection_set.short_description = 'Harvest the collection[s]'