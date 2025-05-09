import json
import requests

# Campuses from Calipshere public_interface.constants
CAMPUS_LIST = [
    {
        'featuredImage': {
            'src': '/thumb-uc_berkeley.jpg',
            'url': '/item/ark:/13030/ft400005ht/'
        },
        'id': '1',
        'name': 'UC Berkeley',
        'slug': 'UCB'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_davis.jpg',
            'url': '/item/ark:/13030/kt6779r95t/'
        },
        'id': '2',
        'name': 'UC Davis',
        'slug': 'UCD'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_irvine.jpg',
            'url': '/item/ark:/13030/hb6s2007ns/'
        },
        'id': '3',
        'name': 'UC Irvine',
        'slug': 'UCI'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_la.jpg',
            'url': '/item/ark:/21198/zz002bzhj9/'
        },
        'id': '10',
        'name': 'UCLA',
        'slug': 'UCLA'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_merced.jpg',
            'url': '/item/630a2224-a666-47ab-bd51-cda382108b6a/'
        },
        'id': '4',
        'name': 'UC Merced',
        'slug': 'UCM'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_riverside.jpg',
            'url': '/item/3669304d-960c-4c1d-b870-32c9dc3b288b/'
        },
        'id': '5',
        'name': 'UC Riverside',
        'slug': 'UCR'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_sandiego.jpg',
            'url': '/item/ark:/20775/bb34824128/'
        },
        'id': '6',
        'name': 'UC San Diego',
        'slug': 'UCSD'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_sf-v2.jpg',
            'url': '/item/3fe65b42-122e-48de-8e4b-bc8dcf531216/'
        },
        'id': '7',
        'name': 'UC San Francisco',
        'slug': 'UCSF'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_santabarbara.jpg',
            'url': '/item/ark:/13030/kt00003279/'
        },
        'id': '8',
        'name': 'UC Santa Barbara',
        'slug': 'UCSB'
    },
    {
        'featuredImage': {
            'src': '/thumb-uc_santacruz.jpg',
            'url': '/item/ark:/13030/hb4b69n74p/'
        },
        'id': '9',
        'name': 'UC Santa Cruz',
        'slug': 'UCSC'
    }
]

host = "registry"
# host = "registry-stg"

api = f"https://{host}.cdlib.org/api/v1/"

def json_loads_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch data: {resp.status_code}")
    return resp.json()

def get_campus_data():
    oac_data = {}
    for campus in CAMPUS_LIST:
        registry_details = json_loads_url(
            f"{api}/campus/{campus.get('id')}/?format=json")
        if registry_details.get('ark'):
            contact_info = json_loads_url(
                "http://dsc.cdlib.org/institution-json/" +
                registry_details.get('ark'))
        else:
            contact_info = {}
        oac_data[campus.get('id')] = contact_info
    with open(f"{host}/campus_oac_data.json", "w") as f:
        json.dump(oac_data, f, indent=4)


# Repository:

def get_repository_data():
    base = f"https://{host}.cdlib.org"
    url = "/api/v1/repository/?format=json&limit=50"
    page = 0
    while url:
        response = json_loads_url(f"{base}{url}")
        oac_data = {}
        for repo in response.get('objects', []):
            contact_info = {}
            if repo.get('ark'):
                resp = requests.get(
                    "http://dsc.cdlib.org/institution-json/" +
                    repo.get('ark')
                )
                if resp.status_code != 200:
                    print(
                        f"Failed to fetch data: {resp.status_code} "
                        "for url http://dsc.cdlib.org/institution-json/" +
                        repo.get('ark') + " for repo " + repo.get('name') +
                        " with id " + str(repo.get('id'))
                    )
                    contact_info = {}
                else:
                    contact_info = resp.json()
            else:
                print(
                    f"No ark for repo {repo.get('name')} with id "
                    f"{repo.get('id')}, skipping."
                )
            oac_data[repo.get('id')] = contact_info
        with open(f"{host}/repo_oac_data/repo_oac_data-{page}.json", 'w') as f:
            json.dump(oac_data, f, indent=4)
        page += 1
        url = response.get('meta', {}).get('next')

