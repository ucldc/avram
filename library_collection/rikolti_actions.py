from django.utils.safestring import mark_safe
import django.contrib.messages as messages
from .models import HarvestTrigger

from .mwaa_client import get_mwaa_cli_token, cli_trigger_dag
from . import opensearch_client as opensearch


def trigger_job(collection, dag_id, mwaa, configuration):
    mwaa_dag_trigger = cli_trigger_dag(mwaa, dag_id, configuration)
    harvest_trigger = HarvestTrigger(
        collection=collection,
        dag_id=dag_id,
        hostname=mwaa.hostname,
        stdout=mwaa_dag_trigger.resp.stdout,
        stderr=mwaa_dag_trigger.resp.stderr,
        dag_run_id=mwaa_dag_trigger.dag_run_id,
        airflow_execution_time=mwaa_dag_trigger.logical_date
    )
    harvest_trigger.save()
    return harvest_trigger


def mwaa_success_message(harvest_trigger):
    return (
        f"✅ <a href='{harvest_trigger.collection.admin_url()}'>"
        f"{harvest_trigger.collection}</a> - Airflow Link: "
        f"<a href='{harvest_trigger.dag_run_link}'>"
        f"{harvest_trigger.dag_run_id}</a> - Log Output: "
        f"<a href='{harvest_trigger.admin_url()}'>Trigger</a>"
    )


def mwaa_failure_message(harvest_trigger):
    return (
        f"⛔ There was a MWAA error trying to run {harvest_trigger.dag_id} "
        f"for <a href='{harvest_trigger.collection.admin_url()}'>"
        f"{harvest_trigger.collection}</a> - check log output: "
        f"<a href='{harvest_trigger.admin_url()}'>harvest trigger</a>"
    )


def registry_failure_message(collection, e):
    return (
        "⛔ Something went wrong registry-side for collection "
        f"<a href='{collection.admin_url()}'>{collection}</a> - {str(e)}"
    )


def harvest_collection_set(modeladmin, request, queryset):
    """Try to trigger the harvest_collection DAG for each collection
    in the queryset. Report any errors - both MWAA side and registry side - out
    to the user via the Admin interface message system."""

    mwaa = get_mwaa_cli_token()
    dag_id = 'harvest_collection'
    user_message = []
    message_level = messages.SUCCESS
    successful_triggers = 0

    for collection in queryset:
        dag_conf = f"'{{\"collection_id\": \"{collection.id}\"}}'"
        try:
            harvest_trigger = trigger_job(collection, dag_id, mwaa, dag_conf)
            if harvest_trigger.stderr:
                user_message.append(mwaa_failure_message(harvest_trigger))
                message_level = messages.WARNING
            else:
                user_message.append(mwaa_success_message(harvest_trigger))
                successful_triggers += 1
        except Exception as e:
            user_message.append(registry_failure_message(collection, e))
            message_level = messages.WARNING

    if successful_triggers == 0:
        message_level = messages.ERROR

    user_message = '<br/>'.join(user_message)
    modeladmin.message_user(request, mark_safe(
        f"Started {successful_triggers} of {len(queryset)} "
        f"harvests: <br/>{user_message}"
    ), level=message_level)

harvest_collection_set.short_description = 'Harvest the collection[s]'


def valid_staged_version(staged_versions):
    # verify that staged_version is a list of strings of length 1
    if isinstance(staged_versions, dict) and len(staged_versions) == 1:
        return list(staged_versions.keys())[0]
    else:
        raise ValueError(
            "Invalid staged_versions, not sure what to publish: "
            f"{staged_versions}"
        )


def publish_collection_set(modeladmin, request, queryset):
    """Try to trigger the publish_collection DAG for each collection
    in the queryset. Report any errors - both MWAA side and registry side - out
    to the user via the Admin interface message system."""

    mwaa = get_mwaa_cli_token()
    dag_id = 'publish_collection'
    user_message = []
    message_level = messages.SUCCESS
    successful_triggers = 0

    for collection in queryset:
        try:
            staged_versions = opensearch.get_versions('rikolti-stg', collection)
            staged_version = valid_staged_version(staged_versions)
            collection.production_target_version = staged_version
            collection.save()
            dag_conf = (
                f"'{{\"collection_id\": \"{collection.id}\", "
                f"\"version\": \"{staged_version}\"}}'"
            )
            harvest_trigger = trigger_job(collection, dag_id, mwaa, dag_conf)
            if harvest_trigger.stderr:
                user_message.append(mwaa_failure_message(harvest_trigger))
                message_level = messages.WARNING
            else:
                user_message.append(mwaa_success_message(harvest_trigger))
                successful_triggers += 1
        except Exception as e:
            user_message.append(registry_failure_message(collection, e))
            message_level = messages.WARNING

    if successful_triggers == 0:
        message_level = messages.ERROR

    user_message = '<br/>'.join(user_message)
    modeladmin.message_user(request, mark_safe(
        f"Started {successful_triggers} of {len(queryset)} "
        f"publish_collection jobs: <br/>{user_message}"
    ), level=message_level)

publish_collection_set.short_description = 'Publish staged collection[s]'
