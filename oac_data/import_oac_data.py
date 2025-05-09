import json
from library_collection.models import Campus, Repository

host = "registry"
# host = "registry-stg"

# open file campus_oac_data.json
def read_campus_oac_data():
    with open(f'oac_data/{host}/campus_oac_data.json', 'r') as file:
        oac_campus_data = json.load(file)
    for campus_id, campus_data in oac_campus_data.items():
        yield campus_id, campus_data


def import_campus_oac_data():
    """
    Import OAC data into the Campus model.
    
    Campus OAC data includes 'name', 'ark', and 'ga' fields, which 
    should match the 'name', 'ark', and 'google_analytics_tracking_code'
    fields in the Campus model respectively. 
    """
    for campus_id, oac_data in read_campus_oac_data():
        campus = Campus.objects.get(pk=campus_id)

        if (
            campus and
            campus.name == oac_data.get('name') and 
            campus.ark == oac_data.get('ark') and
            campus.google_analytics_tracking_code == oac_data.get('ga')
        ):
            print(f"Campus found: {campus_id}: {campus.name}")
            campus.address1 = oac_data.get('address1')
            campus.address2 = oac_data.get('address2')
            campus.city = oac_data.get('city')
            campus.county = oac_data.get('county')
            campus.zip4 = oac_data.get('zip4')
            campus.url = oac_data.get('url')
            campus.phone = oac_data.get('phone')
            campus.fax = oac_data.get('fax')
            campus.email = oac_data.get('email')
            campus.latitude = oac_data.get('latitude')
            campus.longitude = oac_data.get('longitude')
            campus.description = oac_data.get('description')
            campus.save()
        else:
            print("Campus not found or data mismatch for campus_id:", campus_id)


def read_repository_oac_data():
    # these are paginated in files called repo_oac_data-0.json, 
    # repo_oac_data-1.json, etc. - we need to read all of them
    page = 0
    while True:
        try:
            with open(f'oac_data/{host}/repo_oac_data/repo_oac_data-{page}.json', 'r') as file:
                oac_repo_data = json.load(file)
            for repo_id, repo_data in oac_repo_data.items():
                yield repo_id, repo_data
            page += 1
        except FileNotFoundError:
            break


def import_repository_oac_data():
    """
    Import OAC data into the Repository model.

    Repository OAC data includes 'name', 'ark', and 'parent' fields, which
    should match the 'ark' field in the Repository model.
    """
    for repo_id, oac_data in read_repository_oac_data():
        if not oac_data:
            continue
        try:
            repo = Repository.objects.get(pk=repo_id)
        except Repository.DoesNotExist:
            print("Repository not found for repository_id:", repo_id)
            continue

        # checking the Registry's campus against OAC's parent isn't a good 
        # check, since institutions like Stanford exist in OAC, but not in 
        # Calisphere. commenting it out after looking at the data. 
        # campus = repo.campus.all()
        # campus_names = [c.name for c in campus]
        # if (
        #     oac_data.get('parent') not in campus_names and
        #     not (oac_data.get('parent') == None and len(campus_names) == 0)
        # ):
        #     print(
        #         f"Campus name mismatch for repository_id: {repo_id}"
        #         f" - {oac_data.get('parent')} in {campus_names}: {oac_data.get('parent') in campus_names}"
        #     )
        #     continue

        # checking oac's name against registry's name isn't a good check, 
        # since Calisphere frequently appends a prefix to the name, or changes
        # some of the punctuation. This was a useful report, though. I ran 
        # through the 39 cases where the name didn't match and all were
        # acceptable. 
        # name_condition = (oac_data.get('name') and oac_data.get('name') in repo.name)
        # name_condition and 

        if (
            repo and
            repo.ark == oac_data.get('ark')
        ):
            print(f"Dry run - Repository found: {repo_id}: {repo.name}")
            # Uncomment the following lines to update the repository data
            # repo.address1 = oac_data.get('address1')
            # repo.address2 = oac_data.get('address2')
            # repo.city = oac_data.get('city')
            # repo.county = oac_data.get('county')
            # repo.zip4 = oac_data.get('zip4')
            # repo.url = oac_data.get('url')
            # repo.phone = oac_data.get('phone')
            # repo.fax = oac_data.get('fax')
            # repo.email = oac_data.get('email')
            # repo.latitude = oac_data.get('latitude')
            # repo.longitude = oac_data.get('longitude')
            # repo.description = oac_data.get('description')
            # repo.save()
        else:
            if not repo:
                print("Repository not found for repository_id:", repo_id)
            # if not name_condition:
            #     print(
            #         "ERROR: Repository name mismatch for " 
            #         f"repository_id: {repo_id}\n"
            #         f" - {oac_data.get('name')} in {repo.name}: {name_condition}\n"
            #     )
            if repo.ark != oac_data.get('ark'):
                print(
                    "ERROR: Repository ark mismatch for " 
                    f"repository_id: {repo_id}\n"
                    f" - {repo.ark} == {oac_data.get('ark')}: {repo.ark == oac_data.get('ark')}\n"
                )