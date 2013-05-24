"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from urllib import quote
from django.test import TestCase
from library_collection.models import *
from django.contrib.auth.models import User
#from library_collection.admin import URLFieldsListFilter


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

class ProvenancialCollectionAdminTestCase(TestCase):
    '''Check that the list filter is defined correctly. Will need test
    fixtures here.
    '''
    def setUp(self):
        pc = ProvenancialCollection()
        pc.name = 'PC-1'
        pc.url_local = 'http://local'
        pc.save()
        pc = ProvenancialCollection()
        pc.name = 'PC-2'
        pc.url_oac = 'http://oac'
        pc.save()
        u = User.objects.create_user('test', 'mark.redar@ucop.edu', password='fake')
        u.is_superuser = True
        u.is_active = True
        u.is_staff = True #needs to be staff to access admin
        u.save()

    def testURLFieldsListFilter(self):
        '''Test that the URL fields filter works'''
        #setup some datas, use fixtures once fixtures in place
        url_admin = '/admin/library_collection/provenancialcollection/'
        response = self.client.get(url_admin)
        self.assertContains(response, 'Password')
        ret = self.client.login(username='test', password='fake')
        self.failUnless(ret)
        response = self.client.get(url_admin)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        response = self.client.get(url_admin+'?urlfields=LOCALNOT')
        self.assertNotContains(response, 'Password')
        self.assertNotContains(response, 'PC-1')
        self.assertContains(response, 'PC-2')
        response = self.client.get(url_admin+'?urlfields=OACNOT')
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')
