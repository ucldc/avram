# run python manage.py shell
# >>> execfile('library_collection/util/dump_repos_to_csv.py)
# writes to repos.csv
import csv
import codecs
from library_collection.models import Repository

with codecs.open('repos.csv', 'w', 'utf8') as fooout:
    writer = csv.writer(fooout, dialect="excel-tab")
    for r in Repository.objects.all():
        writer.writerow((r.name, r.campus.all()))
