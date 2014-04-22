"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from urllib import quote
import unittest
from django.conf import settings
from django.test import TestCase
from django_webtest import WebTest
from library_collection.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
#from library_collection.admin import URLFieldsListFilter
from mock import patch
from library_collection.models import Collection
from library_collection.models import Campus
from library_collection.models import Repository
from library_collection.models import Status
from library_collection.models import Restriction
from library_collection.models import Need

def skipUnlessIntegrationTest(selfobj=None):
    '''Skip the test unless the environmen variable RUN_INTEGRATION_TESTS is set.
    '''
    if os.environ.get('RUN_INTEGRATION_TESTS', False):
        return lambda func: func
    return unittest.skip('RUN_INTEGRATION_TESTS not set. Skipping integration tests.')

class CollectionTestCase(TestCase):
    fixtures = ('collection.json', 'initial_data.json', 'repository.json')
    def setUp(self):
        c = Collection.objects.all()[0]
        c.status = Status.objects.get(id=1)
        c.access_restrictions = Restriction.objects.get(id=1)
        c.need_for_dams  = Need.objects.get(id=1)
        c.save()

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
        self.assertTrue(hasattr(pc, 'url_harvest'))
        self.assertTrue(hasattr(pc, 'harvest_type'))
        self.assertTrue(hasattr(pc, 'harvest_extra_data'))
        self.assertTrue(hasattr(pc, 'enrichments_item'))
        pc.save()
        pc.repository

    def test_linked_data(self):
        c = Collection.objects.all()[0]
        self.assertEqual(str(c.status), 'Completed')
        self.assertEqual(str(c.access_restrictions), 'No')
        self.assertEqual(str(c.need_for_dams), 'High')
        self.assertTrue(hasattr(c, 'url_api'))
        self.assertIsNotNone(c.url_api)
        self.assertEqual(c.url_api, '/api/v1/collection/1/')

    @skipUnlessIntegrationTest()
    def test_start_harvest_integration(self):
        pc = Collection.objects.all()[0]
        u = User.objects.create_user('test', 'mark.redar@ucop.edu', password='fake')
        pc.url_oai = 'http://example.com/oai'
        pc.url_harvest = 'http://example.com/oai'
        pc.harvest_extra_data = 'testset'
        pc.save()
        retVal = pc.start_harvest(u)
        self.assertTrue(isinstance(retVal, int))
        with patch('subprocess.Popen') as mock_subprocess:
            retVal = pc.start_harvest(u)
            self.assertTrue(mock_subprocess.called)
            mock_subprocess.assert_called_with([pc.harvest_script, 'mark.redar@ucop.edu',
                '/api/v1/collection/1/']
                )


    def test_start_harvest_function(self):
        '''
        Test of harvest starting function. Kicks off a "harvest" for the 
        given collection.
        '''
        pc = Collection.objects.all()[0]
        self.assertTrue(hasattr(pc, 'start_harvest'))
        u = User.objects.create_user('test', 'mark.redar@ucop.edu', password='fake')
        pc.harvest_script = 'xxxxx'
        pc.url_oai = 'http://example.com/oai'
        pc.url_harvest = 'http://example.com/oai'
        pc.harvest_extra_data = 'testset'
        pc.save()
        self.assertRaises(OSError, pc.start_harvest, u)
        pc.harvest_script = 'true'
        retVal = pc.start_harvest(u)
        self.assertTrue(isinstance(retVal, int))
        with patch('subprocess.Popen') as mock_subprocess:
            retVal = pc.start_harvest(u)
            self.assertTrue(mock_subprocess.called)
            mock_subprocess.assert_called_with(['true', 'mark.redar@ucop.edu',
                '/api/v1/collection/1/']
                )


class CollectionModelAdminTestCase(unittest.TestCase):
    '''Use the basic unit test case to test some facts about the 
    CollectionAdmin model.
    '''
    def testAdminHasStartHarvestAction(self):
        '''Test that the admin interface has a start harvest action
        '''
        from library_collection.admin import start_harvest
        from library_collection.admin import CollectionAdmin
        self.assertTrue(start_harvest in CollectionAdmin.actions)


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
        pc = Collection()
        pc.name = 'PC-3'
        pc.url_local = 'http://local'
        pc.save()
        pc = Collection()
        pc.name = 'PC-4'
        pc.url_oai = 'http://oai'
        pc.save()
        u = User.objects.create_user('test', 'mark.redar@ucop.edu', password='fake')
        u.is_superuser = True
        u.is_active = True
        u.is_staff = True #needs to be staff to access admin
        u.save()

    def testURLFieldsListFilter(self):
        '''Test that the URL fields filter works'''
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
        self.assertNotContains(response, '&lt;function')
        response = self.client.get(url_admin+'?urlfields=LOCAL', HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')
        self.assertContains(response, 'PC-3')
        self.assertContains(response, 'class="row1"', count=1)
        self.assertContains(response, 'class="row2"', count=1)
        response = self.client.get(url_admin+'?urlfields=OACNOT', HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')
        self.assertContains(response, 'class="row1"', count=2)

    def testUserListHasRequiredColumns(self):
        '''Test that the "active" column is present in the admin user list
        view.
        '''
        url_admin = '/admin/auth/user/'
        http_auth = 'basic '+'test:fake'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username")
        self.assertContains(response, "Active")
        self.assertContains(response, "Email")
        self.assertContains(response, "Date joined")
        self.assertContains(response, "Staff status")


class CollectionAdminHarvestTestCase(WebTest):
    '''Test the start harvest action on the collection list admin page
    '''
    fixtures = ('collection.json', 'initial_data.json', 'repository.json', 'user.json', 'group.json')
    def testStartHarvestActionAvailable(self):
        '''Test that the start harvest action appears on the collection
        admin list page
        '''
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic '+'test_user_super:test_user_super'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'start_harvest')

    @patch.object(Collection, 'start_harvest')
    def testStartHarvestOnCollections(self, mock):
        '''Test that the user can select & start the harvest for a number of
        collections
        '''
        url_admin = '/admin/library_collection/collection/?urlfields=OAI'
        http_auth = 'basic '+'test_user_super:test_user_super'.encode('base64')
        #response = self.app.get(url_admin, user='test_user_super', HTTP_AUTHORIZATION=http_auth)
        response = self.app.get(url_admin, headers={'AUTHORIZATION':http_auth})
        form =  response.forms['changelist-form']
        form.action = '.' #set to "" in html, need to point to . for WebTest
        select_action = form.fields['action'][0]
        select_action.value = 'start_harvest'
        #check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        #TODO: Unclear how to test that function is actually run....
        resp = form.submit('index', headers={'AUTHORIZATION':http_auth})
        self.assertEqual(resp.status_int, 302)
        self.assertTrue(mock.called)
        self.assertTrue(mock.call_count == 3)

    def testStartHarvestOnCollectionErrorMessages(self):
        '''Test that the start harvest action creates reasonable error
        messages when it fails
        '''
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic '+'test_user_super:test_user_super'.encode('base64')
        response = self.app.get(url_admin, headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 200)
        form =  response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'start_harvest'
        #check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION':http_auth})
        self.assertContains(response, 'Not a harvestable collection', count=3)
        self.assertContains(response, 'Not a harvestable collection - UCSB Libraries Digital Collections')
        self.assertContains(response, 'Not a harvestable collection - Cholera Collection')
        self.assertContains(response, 'Not a harvestable collection - Paul G. Pickowicz Collection of Chinese Cultural Revolution Posters')
        url_admin = '/admin/library_collection/collection/?urlfields=OAI'
        response = self.app.get(url_admin, headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 200)
        form =  response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'start_harvest'
        #check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        Collection.harvest_script = 'xxxx'
        response = form.submit('index', headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertContains(response, 'Cannot find executable xxxx', count=3)
        Collection.harvest_script = 'true'
        form =  response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'start_harvest'
        #check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION':http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertNotContains(response, 'Cannot find executable')
        self.assertContains(response, 'Started harvest for Harold Scheffler Papers (Melanesian Archive) (PID= ')
        self.assertContains(response, 'Started harvest for AIDS Poster collection (PID= ')
        self.assertContains(response, 'Started harvest for Los Angeles Times Photographic Archive (PID= ')


class RepositoryTestCase(TestCase):
    '''Test the base repository model'''
    #No point until some non-standard Django behavior needed
    def testRepositoryModelExists(self):
        r = Repository()
        r.name = "test repo"
        r.save()
        self.assertTrue(hasattr(r, 'slug'))
        self.assertTrue(hasattr(r, 'ark'))

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
        self.assertContains(response, '"campus":', count=203)
        self.assertContains(response, '"repository":', count=188)
        self.assertContains(response, '"slug":', count=399)
        self.assertContains(response, '"url_oai":', count=188)
        self.assertContains(response, 'appendix":', count=188)
        #now check some specific instance data?
        self.assertContains(response, '"name":', count=399)
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
        self.assertContains(response, 'UC Berkeley')
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

class CampusTestCase(TestCase):
    fixtures = ('initial_data.json',)
    def testCampusSlugStartsWithUC(self):
        c = Campus()
        c.name = 'test'
        c.slug = 'test'
        self.assertRaises(ValueError, c.save)
        c.slug = 'UCtest'
        c.save()
        self.assertTrue(hasattr(c, 'ark'))

    def testCampusARKCorrect(self):
        c = Campus.objects.get(pk=1)
        self.assertEqual(c.slug, 'UCB')
        self.assertEqual(c.ark, 'ark:/13030/tf0p3009mq')

    def testNoDupArks(self):
        '''Need to programatically check that the arks are unique.
        Due to the need for blank arks (django weird char null), we can't 
        use the DB unique property.
        '''
        c = Campus()
        c.name = 'test'
        c.slug = 'UCtest'
        c.ark = 'ark:/13030/tf0p3009mq'
        self.assertRaises(ValueError, c.save)
        try:
            c.save()
        except ValueError, e:
            self.assertEqual(e.args, ('Campus with ark ark:/13030/tf0p3009mq already exists',))
        c.ark = ''
        c.save()
        c2 = Campus()
        c2.name = 'test2'
        c2.slug = 'UCtest2'
        c2.ark = ''
        c2.save()

        
class PublicViewNewCampusTestCase(TestCase):
    '''Test the public view immediately after a new campus added. fails if
    no collections for a campus
    NOTE: You need to run this test separate from the other tests to get
    the reverse lookup fail, otherwise it just doesn't find the NTC at all,
    don't know why...
    '''
    fixtures = ('collection.json', 'initial_data.json', 'repository.json')
    def setUp(self):
        c = Campus()
        c.name = "New Test Campus"
        c.slug = "NTC"
        c.order = 200
        self.assertRaises(ValueError, c.save)

    def testRootViewNewCampus(self):
        '''When adding new campuses without a collection, this view fails due
        to a {% url %} tag in the template, forcing a revese lookup that fails.
        This is because as of 2013-12-18, the urls.py has a hard-coded UC in
        the view lookups.
        NOW PROTECTED AGAINST THIS -- 2013-12-18
        '''
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'library_collection/collection_list.html')
        self.assertContains(response, 'UC Berkeley')
        #self.assertContains(response, 'New Test Campus')
        self.assertContains(response, 'collections')
        self.assertContains(response, '/21/w-gearhardt-photographs-photographs-of-newport-bea/">W. Gearhardt photographs')


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
        self.assertContains(response, 'Collections')
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

    def testCollectionViewFormSubmissionEmptyForm(self):
        '''Test form submission to modify a collection with an empty form'''
        url = reverse('edit_detail', 
                kwargs={ 'colid': 2, 
                'col_slug':'halberstadt-collection-selections-of-photographs-p'},
            )
        response = self.client.post(url, {'name': ''}, 
                HTTP_AUTHORIZATION=self.http_auth
            )
        self.assertTemplateUsed(response, 'library_collection/collection_edit.html')
        self.assertContains(response, 'Error:')
        self.assertContains(response, 'Please enter a')

    def testCollectionCreateViewForm(self):
        '''Test form to create a new collection'''
        url = reverse('edit_collections')
        response = self.client.post(url, {'new': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/collection_edit.html')
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
    
    def testCollectionCreateViewFormSubmissionEmptyForm(self):
        '''Test form submission to create an empty collection'''
        url = reverse('edit_collections')
        response = self.client.post(url, {'name': ''}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/collection_edit.html')
        self.assertContains(response, 'Error:')
    
    def testRepositoryCreateViewForm(self):
        '''Test form to create a new repository'''
        url = reverse('edit_repositories')
        response = self.client.post(url, {'edit': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertContains(response, 'Save')
    
    def testRepositoryCreateViewFormSubmission(self):
        '''Test form submission to create a repository'''
        url = reverse('edit_repositories')
        response = self.client.post(url, {'name': 'new repository', 'campuses': ['1', '4']}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertContains(response, 'Add')
        self.assertContains(response, 'new repository')
   
    def testRepositoryCreateViewFormSubmissionEmptyForm(self):
        '''Test form submission to create an empty repository'''
        url = reverse('edit_repositories')
        response = self.client.post(url, {'name': ''}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/repository_list.html')
        self.assertContains(response, 'Error:')
        self.assertContains(response, 'Please enter a unit title')
   
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
        self.assertTemplateUsed(response, 'library_collection/verification_required.html')
        # self.assertEqual(response.status_code, 200)
        #TODO: Test that the new user message page is presented to new user
        # check correct template and view????
