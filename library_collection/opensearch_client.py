import urllib3
from boto3 import Session
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning

from django.conf import settings
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy import AWSV4SignerAuth
from opensearchpy.exceptions import ConnectionError


def verify_certs():
    ignore_tls = settings.OPENSEARCH.get('ignore_tls')
    if ignore_tls:
        urllib3.disable_warnings(InsecureRequestWarning)
    return not ignore_tls


def get_auth():
    es_user = settings.OPENSEARCH.get('user')
    es_pass = settings.OPENSEARCH.get('pass')
    if es_user and es_pass:
        return (es_user, es_pass)

    credentials = Session().get_credentials()
    if not credentials:
        return False
    return AWSV4SignerAuth(
        credentials, settings.OPENSEARCH.get("aws_region", "us-west-2"))


def get_client():
    if not settings.OPENSEARCH:
        raise ValueError("Missing OPENSEARCH in settings")

    host_url = urlparse(settings.OPENSEARCH['endpoint'])

    client = OpenSearch(
        hosts=[{
            'host': host_url.hostname,
            'port': host_url.port or 443,
        }],
        http_auth=get_auth(),
        use_ssl=True,
        verify_certs=verify_certs(),
        ssl_show_warn=verify_certs(),
        connection_class=RequestsHttpConnection,
    )
    return client


def get_versions(alias, collection: 'Collection'):
    if not collection.id:
        return {}
    try:
        client = get_client()
        response = client.search(
            index=alias,
            body={
                'query': {
                    'term': {
                        'collection_id': collection.id
                    }
                },
                'size': 0,
                'aggs': {
                    'published_versions': {
                        'terms': {
                            'field': 'rikolti.version_path',
                            'size': 10
                        }
                    }
                }
            }
        )
    except ConnectionError:
        return f"Unable to connect to OpenSearch @ {settings.OPENSEARCH['endpoint']}"
    except Exception as e:
        return f"Error fetching versions from OpenSearch: {e}"
    versions = response['aggregations']['published_versions']['buckets']
    return {v['key']: v['doc_count'] for v in versions}


def record_count(alias, collection: 'Collection'):
    if not collection.id:
        return 0
    try:
        client = get_client()
        response = client.count(
            index=alias,
            body={
                'query': {
                    'term': {
                        'collection_id': collection.id
                    }
                }
            }
        )
    except ConnectionError:
        return f"Unable to connect to OpenSearch @ {settings.OPENSEARCH['endpoint']}"
    except Exception as e:
        return f"Error fetching versions from OpenSearch: {e}"
    return response['count']

