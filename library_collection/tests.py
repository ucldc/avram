"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from library_collection.models import ProvenancialCollection
from django.test import TestCase


class ProvenancialCollectionTestCase(TestCase):
    def test_basic_addition(self):
        """
        Sanity check on ProvenancialCollection model
        """
        pc = ProvenancialCollection()
        pc.url_local = 'http://www.oac.cdlib.org/'
        pc.extent = 1234567890
        pc.name = 'A test collection'
        self.assertEqual(pc.url, pc.url_local)
        self.assertEqual(pc.human_extent, u'1.1\xa0G')
        self.assertEqual(pc.name, unicode(pc))
