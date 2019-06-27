from . import set_avram_lib_path
from django.contrib.admin import actions

from library_collection.models import Collection
for c in Collection.objects.filter(harvest_type='OAC'):
    c.enrichments_item = c.enrichments_item.strip()
    if 'oac-thumbnail' not in c.enrichments_item:
        c.enrichments_item = ''.join((c.enrichments_item, ',\n/oac-thumbnail'))
    c.enrichments_item = ''.join((c.enrichments_item, ',\n/oac-to-sourceResource'))
    print('Updating collection:{} {}'.format(c.id, c.slug))
    c.save()
