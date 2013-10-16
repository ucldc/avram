"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from urllib import quote
from django.test import TestCase
from library_collection.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
#from library_collection.admin import URLFieldsListFilter


class CollectionTestCase(TestCase):
    def test_basic_addition(self):
        """
        Sanity check on Collection model
        """
        pc = Collection()
        pc.url_local = 'http://www.oac.cdlib.org/'
        pc.extent = 1234567890
        pc.name = 'A test collection'
        self.assertEqual(pc.url, pc.url_local)
        self.assertEqual(pc.human_extent, u'1.1\xa0G')
        self.assertEqual(pc.name, unicode(pc))
        pc.save()
        pc.repository

class CollectionAdminTestCase(TestCase):
    '''Check that the list filter is defined correctly. Will need test
    fixtures here.
    '''
    def setUp(self):
        pc = Collection()
        pc.name = 'PC-1'
        pc.url_local = 'http://local'
        pc.save()
        pc = Collection()
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
        # https://code.djangoproject.com/ticket/13394
        # https://groups.google.com/d/msg/django-users/VpPrGVPS0aw/SwE8X51Q8jYJ
        url_admin = '/admin/library_collection/collection/'
        response = self.client.get(url_admin)
        self.assertEqual(response.status_code, 401)
        # this doesn't work when using the BasicAuthMockMiddleware
        # need to add the http_auth to request to get logged in
        # ret = self.client.login(username='test', password='fake')
        http_auth = 'basic '+'test:fake'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PC-1')
        response = self.client.get(url_admin+'?urlfields=LOCALNOT', HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertNotContains(response, 'PC-1')
        self.assertContains(response, 'PC-2')
        response = self.client.get(url_admin+'?urlfields=OACNOT', HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')


class RepositoryTestCase(TestCase):
    '''Test the base repository model'''
    #No point until some non-standard Django behavior needed
    def testRepositoryModelExists(self):
        r = Repository()
        r.name = "test repo"
        r.save()

class RepositoryAdminTestCase(TestCase):
    '''Test the admin for repository'''
    def setUp(self):
        r = Repository()
        r.name = 'TEST REPO'
        r.save()
        u = User.objects.create_user('test', 'mark.redar@ucop.edu', password='fake')
        u.is_superuser = True
        u.is_active = True
        u.is_staff = True #needs to be staff to access admin
        u.save()

    def testRepoInAdmin(self):
        url_admin = '/admin/library_collection/repository/'
        response = self.client.get(url_admin)
        self.assertEqual(response.status_code, 401)
        http_auth = 'basic '+'test:fake'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'TEST REPO')

class TastyPieAPITest(TestCase):
    '''Verify the tastypie RESTful feed'''
    fixtures = ('collection.json', 'initial_data.json', 'repository.json')
    url_api =  '/api/v1/' #how to get from django?

    def testAPIFeed(self):
        '''Sanity check'''
        response = self.client.get(self.url_api)
        self.assertContains(response, 'collection')

    def testDataInApiFeed(self):
        '''Test that the required data elements appear in the api'''
        url_collection = self.url_api + 'collection/?limit=200&format=json'
        response = self.client.get(url_collection)
        self.assertContains(response, '"collection_type":', count=188)
        self.assertContains(response, '"campus":', count=201)
        self.assertContains(response, '"repository":', count=188)
        self.assertContains(response, '"url_oai":', count=188)
        self.assertContains(response, 'appendix":', count=188)
        #now check some specific instance data?
        self.assertContains(response, '"name":', count=395)
        self.assertContains(response, 'UCD')
        self.assertContains(response, 'eScholarship')
        self.assertContains(response, 'Internet Archive')
        self.assertContains(response, 'Bulletin of Calif. division of Mines and Geology')

class PublicViewTestCase(TestCase):
    '''Test the view for the public'''
    fixtures = ('collection.json', 'initial_data.json', 'repository.json')

    def testRootView(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/collection_list.html')
        self.assertContains(response, 'collections')
        self.assertContains(response, '/21/w-gearhardt-photographs-photographs-of-newport-bea/">W. Gearhardt photographs')
     
    def testUCBCollectionView(self):
        response = self.client.get('/UCB/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'collections')
        self.assertNotContains(response, '/21/w-gearhardt-photographs-photographs-of-newport-bea/">W. Gearhardt photographs')
        self.assertContains(response, '/150/wieslander-vegetation-type-maps-photographs-in-192/')

    def testRepositoriesView(self):
        response = self.client.get('/repositories/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertContains(response, 'Mandeville')

    def testUCBRepositoriesView(self):
        response = self.client.get('/UCB/repositories/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertNotContains(response, 'Mandeville')
        self.assertContains(response, 'Bancroft Library')

    def testCollectionPublicView(self):
        '''Test view of one collection'''
        response = self.client.get('/2/halberstadt-collection-selections-of-photographs-p/')
        self.assertContains(response, 'Halberstadt Collection')
        self.assertContains(response, 'Campus')
        self.assertContains(response, 'Davis')
        self.assertNotContains(response, 'Metadata')

class EditViewTestCase(TestCase):
    '''Test the view for the public'''
    fixtures = ('collection.json', 'initial_data.json', 'repository.json', 'user.json')
    current_app = 'edit'

    def setUp(self):
        self.http_auth = 'basic '+'test_user:test_user'.encode('base64')

    def testRootView(self):
        url = reverse('edit_collections')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/collection_list.html')
        self.assertContains(response, 'collections')
        self.assertContains(response, EditViewTestCase.current_app+'/21/w-gearhardt-photographs-photographs-of-newport-bea/">W. Gearhardt photographs')
     
    def testUCBCollectionView(self):
        url = reverse('edit_collections',
                kwargs={ 'campus_slug':'UCB', }
            )
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'collections')
        self.assertNotContains(response, '/21/w-gearhardt-photographs-photographs-of-newport-bea/">W. Gearhardt photographs')
        self.assertContains(response, EditViewTestCase.current_app+'/150/wieslander-vegetation-type-maps-photographs-in-192/')

    def testRepositoriesView(self):
        url = reverse('edit_repositories')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertContains(response, 'Mandeville')
        self.assertContains(response, '/edit/UCB')
        self.assertContains(response, '/edit/')

    def testUCBRepositoriesView(self):
        url = reverse('edit_repositories',
                kwargs={ 'campus_slug':'UCB', }
            )
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertNotContains(response, 'Mandeville')
        self.assertContains(response, 'Bancroft Library')
        url_edit_base = reverse('edit_collections')
        self.assertContains(response, url_edit_base)
        self.assertContains(response, url_edit_base+'UCB')

    def testCollectionView(self):
        '''Test view of one collection'''
        url = reverse('edit_detail',
                kwargs={ 'colid':2,
                    'col_slug':'halberstadt-collection-selections-of-photographs-p'},
            )
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertContains(response, 'Halberstadt Collection')
        self.assertContains(response, 'Campus')
        self.assertContains(response, 'Davis')
        self.assertNotContains(response, 'Metadata')
        self.assertNotContains(response, 'Bancroft Library')

    def testCollectionViewForm(self):
        '''Test form for modifying a collection'''
        url = reverse('edit_detail', 
                kwargs={ 'colid': 2, 
                'col_slug':'halberstadt-collection-selections-of-photographs-p'},
            )
        response = self.client.post(url, {'edit': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/collection_edit.html')
        self.assertContains(response, 'Save')

    def testCollectionViewFormSubmission(self):
        '''Test form submission to modify a collection'''
        url = reverse('edit_detail', 
                kwargs={ 'colid': 2, 
                'col_slug':'halberstadt-collection-selections-of-photographs-p'},
            )
        response = self.client.post(url, {'appendix': 'A',
                'repositories': '9',
                'name': 'Halberstadt Collection',
                'campuses': ['1', '2']}, 
                HTTP_AUTHORIZATION=self.http_auth
            )
        self.assertTemplateUsed(response, 'library_collection/collection.html')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Berkeley')
        self.assertContains(response, 'Bancroft Library')

    def testCollectionCreateViewForm(self):
        '''Test form to create a new collection'''
        url = reverse('edit_collections')
        response = self.client.post(url, {'edit': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/new_collection.html')
        self.assertContains(response, 'Save')
    
    def testCollectionCreateViewFormSubmission(self):
        '''Test form submission to create a collection'''
        url = reverse('edit_collections')
        response = self.client.post(url, {'appendix': 'B', 
                'repositories': '3', 
                'name': 'new collection', 
                'campuses': ['1', '3']}, 
                HTTP_AUTHORIZATION=self.http_auth
            )
        self.assertTemplateUsed(response, 'library_collection/collection.html')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'new collection')
        self.assertContains(response, 'Berkeley')

class NewUserTestCase(TestCase):
    '''Test the response chain when a new user enters the system.
    With the HttpAuthMockMiddleware, a new user should be authenticated,
    created in the DB and then redirected to the new user message page.
    '''
    #TODO: check workflow for post verification
    fixtures = ('collection.json', 'initial_data.json', 'repository.json', 'user.json', 'group.json')

    def testNewUserAuth(self):
        http_auth = 'basic '+'bogus_new_user:bogus_new_user'.encode('base64')
        url = reverse('edit_collections')
        response = self.client.get(url, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        #TODO: Test that the new user message page is presented to new user
        # check correct template and view????
