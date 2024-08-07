import base64
import os
import re

from typing import NamedTuple
from datetime import datetime
from django.conf import settings

import boto3
import requests

class MwaaConnection(NamedTuple):
    token: str
    hostname: str


class MwaaCliResponse(NamedTuple):
    stdout: str
    stderr: str 


class MwaaDagTrigger(NamedTuple):
    resp: MwaaCliResponse
    dag_run_id: str
    logical_date: datetime


def assume_role(role_arn, role_session_name):
    session = boto3.session.Session()
    sts = session.client('sts')
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name
    )
    cred = resp['Credentials']
    subsession = boto3.session.Session(
        aws_access_key_id=cred['AccessKeyId'],
        aws_secret_access_key=cred['SecretAccessKey'],
        aws_session_token=cred['SessionToken'],
        region_name='us-west-2'
    )
    return subsession


def get_mwaa_cli_token():
    session = assume_role(settings.MWAA_REGISTRY_ROLE_ARN, 'registry-access')
    mwaa_client = session.client('mwaa')
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

    return MwaaCliResponse(stdout, stderr)


def cli_trigger_dag(mwaa, dag_id, dag_conf):
    url = f"https://{mwaa.hostname}/aws_mwaa/cli"
    headers = {
        "Authorization": f"Bearer {mwaa.token}",
        "Content-Type": "text/plain",
    }
    data = f"dags trigger -o yaml {dag_id} -c {dag_conf}"
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 403:
        # maybe our token expired, get a new one and retry:
        mwaa = get_mwaa_cli_token()
        headers['Authorization'] = f"Bearer {mwaa.token}"
        resp = requests.post(url, headers=headers, data=data)

    resp.raise_for_status()
    parsed_resp = parse_cli_resp(resp)
    return MwaaDagTrigger(
        resp=parsed_resp, 
        dag_run_id=find_dag_run_id(parsed_resp.stdout), 
        logical_date=find_logical_date(parsed_resp.stdout)
    )


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

