from django.core.management.base import NoArgsCommand
from django.db.models import Q
from library_collection.models import Collection
from pprint import pprint as pp
import lxml.etree as ET
import os

xslt = ET.XSLT(
    ET.parse(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'oac_description_number.xsl')
        )
    )

class Command(NoArgsCommand):
    help = "Describe the Command Here"

    def handle_noargs(self, **options):
        for collection in Collection.objects.filter(harvest_type='OAC'):
            process_collection(collection)


def process_collection(collection):
    pp(collection)
    ark = collection.url_oac.split("http://www.oac.cdlib.org/findaid/",1)[1]
    res = xslt(ET.parse("http://www.oac.cdlib.org/search?raw=1&identifier={}".format(ark)))
    local_id = res.xpath('//@number')
    description = res.xpath('//text()')

    print(local_id)
    print(description)

    if (not collection.description) and description:
        collection.description = unicode(description[0])

    if local_id:
        collection.local_id = unicode(local_id[0])

    if local_id or ((not collection.description) and description):
        collection.save()
