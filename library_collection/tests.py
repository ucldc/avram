# -*- coding: utf-8 -*-
import os
import unittest
import socket
from base64 import b64encode
from django.test import TestCase
from django_webtest import WebTest
from django.contrib.auth.models import User
from django.urls import reverse
from mock import patch
from library_collection.models import Collection
from library_collection.models import Campus
from library_collection.models import Repository
from .util import sync_oac_collections, sync_oac_repositories
import library_collection.admin_actions
from library_collection.admin_actions import queue_harvest

FILE_DIR = os.path.abspath(os.path.split(__file__)[0])


def skipUnlessIntegrationTest(selfobj=None):
    '''Skip the test unless the environmen variable RUN_INTEGRATION_TESTS is set.
    '''
    if os.environ.get('RUN_INTEGRATION_TESTS', False):
        return lambda func: func
    return unittest.skip(
        'RUN_INTEGRATION_TESTS not set. Skipping integration tests.')


class CollectionTestCase(TestCase):
    fixtures = ['collection.json', 'campus.json', 'repository.json']

    def setUp(self):
        c = Collection.objects.all()[0]
        c.save()

    def test_basic_add_obj(self):
        """
        Sanity check on Collection model
        """
        pc = Collection()
        pc.url_local = 'http://www.oac.cdlib.org/'
        pc.name = 'A test collection'
        self.assertEqual(pc.url, pc.url_local)
        self.assertEqual(pc.name, str(pc))
        self.assertTrue(hasattr(pc, 'url_harvest'))
        self.assertTrue(hasattr(pc, 'harvest_type'))
        self.assertTrue(hasattr(pc, 'harvest_extra_data'))
        self.assertTrue(hasattr(pc, 'enrichments_item'))
        self.assertTrue(hasattr(pc, 'ready_for_publication'))
        self.assertTrue(hasattr(pc, 'rights_status'))
        self.assertTrue(hasattr(pc, 'rights_statement'))
        self.assertFalse(hasattr(pc, 'collection_type'))
        self.assertFalse(hasattr(pc, 'url_was'))
        self.assertFalse(hasattr(pc, 'url_oai'))
        self.assertFalse(hasattr(pc, 'status'))
        self.assertFalse(hasattr(pc, 'access_restrictions'))
        self.assertFalse(hasattr(pc, 'metadata_level'))
        self.assertFalse(hasattr(pc, 'metadata_standard'))
        self.assertFalse(hasattr(pc, 'need_for_dams'))
        self.assertFalse(hasattr(pc, 'appendix'))
        self.assertFalse(hasattr(pc, 'phase_one'))
        self.assertTrue(hasattr(pc, 'local_id'))
        self.assertTrue(hasattr(pc, 'collectioncustomfacet_set'))
        pc.save()
        pc.repository

    def testLongName(self):
        '''In mysql, truncated strings cause saves to fail.
        check that long names are truncated on save
        '''
        c = Collection(name=''.join('x' for i in range(300)))
        c.save()
        self.assertEqual(255, len(c.name))

    def test_linked_data(self):
        c = Collection.objects.all()[0]
        self.assertTrue(hasattr(c, 'url_api'))
        self.assertIsNotNone(c.url_api)
        self.assertIn('/api/v1/collection/1/', c.url_api)
        self.assertIn('https://', c.url_api)

    @skipUnlessIntegrationTest()
    def test_queue_harvest_integration(self):
        pc = Collection.objects.all()[0]
        u = User.objects.create_user(
            'test', 'mark.redar@ucop.edu', password='fake')
        pc.url_harvest = 'http://example.com/oai'
        pc.harvest_extra_data = 'testset'
        pc.save()
        retVal = queue_harvest(u, pc, 'test-queue')
        self.assertTrue(isinstance(retVal, int))
        with patch('subprocess.Popen') as mock_subprocess:
            retVal = queue_harvest(
                    u,
                    'test-queue')
            self.assertTrue(mock_subprocess.called)
            mock_subprocess.assert_called_with([
                pc.harvest_script, 'mark.redar@ucop.edu',
                'https://' + socket.getfqdn() + '/api/v1/collection/1/'
            ])

    @patch('django.contrib.admin.ModelAdmin')
    def test_queue_harvest_function(self, mock_modeladmin):
        '''
        Test of harvest starting function. Kicks off a "harvest" for the
        given collection.
        '''
        pc = Collection.objects.all()[0]
        u = User.objects.create_user(
            'test', 'mark.redar@ucop.edu', password='fake')
        library_collection.admin_actions.HARVEST_SCRIPT = 'xxxxx'
        pc.url_harvest = 'http://example.com/oai'
        pc.harvest_extra_data = 'testset'
        pc.save()
        self.assertRaises(
                TypeError,
                queue_harvest,
                u, pc, 'test-q')

        class Bunch(object):
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        request = Bunch(user=Bunch(email='example@example.edu'))
        pc.harvest_type = 'OAC'
        retVal = queue_harvest(
                mock_modeladmin,
                request,
                [pc],
                'test-q')
        self.assertEqual(
                retVal[0],
                'Cannot find xxxxx for running 1 collections On demand '
                'patron requests')
        self.assertEqual(
                retVal[1],
                False)
        with patch('subprocess.Popen') as mock_subprocess:
            retVal = queue_harvest(mock_modeladmin, request, [pc], 'test-q')
            self.assertTrue(mock_subprocess.called)
            mock_subprocess.assert_called_with([
                'xxxxx', 'example@example.edu', 'test-q',
                'https://' + pc._hostname + '/api/v1/collection/1/'
            ])


class CollectionModelAdminTestCase(unittest.TestCase):
    '''Use the basic unit test case to test some facts about the
    CollectionAdmin model.
    '''

    def testAdminHasQueueHarvestAction(self):
        '''Test that the admin interface has a start harvest action
        '''
        from library_collection.admin import queue_harvest_normal_stage
        from library_collection.admin import CollectionAdmin
        self.assertTrue(queue_harvest_normal_stage in CollectionAdmin.actions)


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
        pc.save()
        u = User.objects.create_user(
            'test', 'mark.redar@ucop.edu', password='fake')
        u.is_superuser = True
        u.is_active = True
        u.is_staff = True  # needs to be staff to access admin
        u.save()

    def testURLFieldsListFilter(self):
        '''Test that the URL fields filter works'''
        url_admin = '/admin/library_collection/collection/'
        response = self.client.get(url_admin)
        self.assertEqual(response.status_code, 401)
        # this doesn't work when using the BasicAuthMockMiddleware
        # need to add the http_auth to request to get logged in
        # ret = self.client.login(username='test', password='fake')
        http_auth = 'basic ' + b64encode('test:fake'.encode()).decode()
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PC-1')
        response = self.client.get(url_admin + '?urlfields=LOCAL',
                                   HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')
        self.assertContains(response, 'PC-3')
        self.assertContains(response, 'class="row1"', count=1)
        self.assertContains(response, 'class="row2"', count=1)
        response = self.client.get(url_admin + '?urlfields=OACNOT',
                                   HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'PC-1')
        self.assertNotContains(response, 'PC-2')
        self.assertContains(response, 'class="row1"', count=2)

    def testHarvestDataInAdmin(self):
        '''Make sure the required harvest data is in the admin interface'''
        url_admin = '/admin/library_collection/collection/1/change/'
        http_auth = 'basic ' + b64encode('test:fake'.encode()).decode()
        # http_auth = 'basic ' + 'test:fake'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'harvest_type')
        self.assertContains(response, 'url_harvest')
        self.assertContains(response, 'harvest_extra_data')
        self.assertContains(response, 'enrichments_item')

    def testUserListHasRequiredColumns(self):
        '''Test that the "active" column is present in the admin user list
        view.
        '''
        url_admin = '/admin/auth/user/'
        http_auth = 'basic ' + b64encode('test:fake'.encode()).decode()
        # http_auth = 'basic ' + 'test:fake'.encode('base64')
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
    fixtures = ('collection.json', 'campus.json', 'repository.json',
                'user.json', 'group.json')

    def testQueueHarvestActionAvailable(self):
        '''Test that the start harvest action appears on the collection
        admin list page
        '''
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()
        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
            # 'base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'queue_harvest')

    def testQueueHarvestOnCollections(self):
        '''Test that the user can select & start the harvest for a number of
        collections
        '''
        url_admin = '/admin/library_collection/collection/?urlfields=OAI'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()
        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
            # 'base64')
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        form = response.forms['changelist-form']
        form.action = '.'  # set to "" in html, need to point to . for WebTest
        select_action = form.fields['action'][0]
        select_action.value = 'queue_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        # TODO: Unclear how to test that function is actually run....
        resp = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(resp.status_int, 302)

    def testQueueHarvestOnCollectionErrorMessages(self):
        '''Test that the start harvest action creates reasonable error
        messages when it fails
        '''
        # c = Collection()
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()
        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
        #     'base64')
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})

        self.assertContains(response, '2 collections not harvestable.')
        self.assertContains(response, '188 UCSB Libraries Digital')
        self.assertContains(response, 'Collections - Invalid harvest type')
        self.assertContains(response, '187 Cholera Collection - Invalid')
        self.assertContains(response, 'A is for atom, B is for bomb')
        url_admin = '/admin/library_collection/collection/?' \
                    'harvest_type__exact=OAC'
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        library_collection.admin_actions.HARVEST_SCRIPT = 'xxxx'
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertContains(response,
                            'Cannot find xxxx for running 3 collections')
        library_collection.admin_actions.HARVEST_SCRIPT = 'true'
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertNotContains(response, 'Cannot find ')
        self.assertContains(response, 'Queued true for 3 ')
        self.assertContains(response, 'collections: &quot;A is for atom,')
        self.assertContains(response, 'Harold Scheffler Papers')
        self.assertContains(response, '(Melanesian Archive)  |  ')
        self.assertContains(response, 'Los Angeles Times Photographic')
        self.assertContains(response, 'mark.redar@ucop.edu normal-stage')
        self.assertContains(response, 'https://registry.cdlib.org/api/v1/'
                                      'collection/189/;')
        self.assertContains(response, 'https://registry.cdlib.org/api/v1/'
                                      'collection/172/;')
        self.assertContains(response, 'https://registry.cdlib.org/api/v1/'
                                      'collection/153/')

    def testQueueHarvestDifferentQueuesActionAvailable(self):
        '''test that there are a number of known queues to add
        harvest to.
        '''
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()

        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
        #     'base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'queue_harvest_normal_stage')

    def testQueueImageHarvestOnCollections(self):
        '''Test that the user can select & start the harvest for a number of
        collections
        '''
        url_admin = '/admin/library_collection/collection/?urlfields=OAI'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()

        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
        #     'base64')
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        form = response.forms['changelist-form']
        form.action = '.'  # set to "" in html, need to point to . for WebTest
        select_action = form.fields['action'][0]
        select_action.value = 'queue_image_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        # TODO: Unclear how to test that function is actually run....
        resp = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(resp.status_int, 302)

    def testQueueImageHarvestOnCollectionErrorMessages(self):
        '''Test that the start harvest action creates reasonable error
        messages when it fails
        '''
        c = Collection()
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()

        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
        #     'base64')
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_image_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})
        self.assertContains(response, 'A is for atom, B is for bomb')
        url_admin = '/admin/library_collection/collection/?' \
                    'harvest_type__exact=OAC'
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_image_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        library_collection.admin_actions.IMAGE_HARVEST_SCRIPT = 'xxxx'
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertContains(
            response, 'Cannot find xxxx for running 3 collections')
        library_collection.admin_actions.IMAGE_HARVEST_SCRIPT = 'true'
        response = self.app.get(url_admin,
                                headers={'AUTHORIZATION': http_auth})
        form = response.forms['changelist-form']
        select_action = form.fields['action'][0]
        select_action.value = 'queue_image_harvest_normal_stage'
        # check a few of harvestable collections
        form.fields['_selected_action'][0].checked = True
        form.fields['_selected_action'][1].checked = True
        form.fields['_selected_action'][2].checked = True
        response = form.submit('index', headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 302)
        response = response.follow(headers={'AUTHORIZATION': http_auth})
        self.assertEqual(response.status_int, 200)
        self.assertNotContains(response, 'Cannot find ')
        self.assertContains(response, ''.join(
            ('Queued true for 3 ',
             'collections: &quot;A is for atom, B is for bomb&quot; video',
             ' tape  |  Harold Scheffler Papers (Melanesian Archive)  |  ',
             'Los Angeles Times Photographic Archive CMD: true ',
             'mark.redar@ucop.edu normal-stage ',
             'https://{0}/api/v1/collection/189/;',
             'https://{0}/api/v1/collection/172/;',
             'https://{0}/api/v1/collection/153/')).format(c._hostname))

    def testQueueImageHarvestDifferentQueuesActionAvailable(self):
        '''test that there are a number of known queues to add
        harvest to.
        '''
        url_admin = '/admin/library_collection/collection/'
        http_auth = 'basic ' + b64encode('test_user_super:test_user_super'.encode()).decode()

        # http_auth = 'basic ' + 'test_user_super:test_user_super'.encode(
        #     'base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'queue_image_harvest_normal_stage')


class RepositoryTestCase(TestCase):
    '''Test the base repository model'''

    # No point until some non-standard Django behavior needed
    def testRepositoryModelExists(self):
        r = Repository()
        r.name = "test repo"
        r.save()
        self.assertTrue(hasattr(r, 'slug'))
        self.assertTrue(hasattr(r, 'ark'))
        self.assertTrue(hasattr(r, 'google_analytics_tracking_code'))

    def testRepositoryNoDupArks(self):
        '''Check that the Repostiories can't have duplicate arks.
        Again, since it is a char & we allow blank, can't use db unique
        check'''
        r = Repository()
        r.name = "test repo"
        r.ark = "fakeARK"
        r.save()
        r2 = Repository()
        r2.name = "test repo"
        r2.ark = "fakeARK"
        self.assertRaises(ValueError, r2.save)
        try:
            r2.save()
        except ValueError as e:
            self.assertEqual(e.args,
                             ('Unit with ark fakeARK already exists', ))
        r2.ark = ''
        r2.save()
        r3 = Repository()
        r3.name = "test repo"
        r3.ark = ''
        r3.save()


class RepositoryAdminTestCase(TestCase):
    '''Test the admin for repository'''

    def setUp(self):
        r = Repository()
        r.name = 'TEST REPO'
        r.save()
        u = User.objects.create_user(
            'test', 'mark.redar@ucop.edu', password='fake')
        u.is_superuser = True
        u.is_active = True
        u.is_staff = True  # needs to be staff to access admin
        u.save()

    def testRepoInAdmin(self):
        url_admin = '/admin/library_collection/repository/'
        response = self.client.get(url_admin)
        self.assertEqual(response.status_code, 401)
        http_auth = 'basic ' + b64encode('test:fake'.encode()).decode()

        # http_auth = 'basic ' + 'test:fake'.encode('base64')
        response = self.client.get(url_admin, HTTP_AUTHORIZATION=http_auth)
        self.assertNotContains(response, 'Password')
        self.assertContains(response, 'TEST REPO')


class TastyPieAPITest(TestCase):
    '''Verify the tastypie RESTful feed'''
    fixtures = ('collection.json', 'campus.json', 'repository.json',
                'collectioncustomfacet.json')
    url_api = '/api/v1/'  # how to get from django?

    def testAPIFeed(self):
        '''Sanity check'''
        response = self.client.get(self.url_api)
        self.assertContains(response, 'collection')

    def testDataInApiFeed(self):
        '''Test that the required data elements appear in the api'''
        url_collection = self.url_api + 'collection/?limit=200&format=json'
        response = self.client.get(url_collection)
        self.assertContains(response, '"campus":', count=204)
        self.assertContains(response, '"repository":', count=189)
        self.assertContains(response, '"slug":', count=400)
        self.assertContains(response, '"url_harvest":', count=189)
        # now check some specific instance data?
        self.assertContains(response, '"name":', count=400)
        self.assertContains(response, 'UCD')
        self.assertContains(response, 'eScholarship')
        self.assertContains(response, 'Internet Archive')
        self.assertContains(response,
                            'Bulletin of Calif. division of Mines and Geology')

    def testFilterOnURL_harvest(self):
        '''Test that we can filter'''
        url_collection = self.url_api + 'collection/?limit=200&' \
                                        'url_harvest__startswith=http'
        response = self.client.get(url_collection)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"total_count": 14}')
        self.assertContains(response, '"next": null')
        self.assertContains(
            response, '"url_harvest": "http://archive.org/services/oai2.php"')

    def testFilterOnSLUG(self):
        '''Test that we can filter'''
        url_collection = self.url_api + 'collection/?limit=200&' \
                                        'slug=halberstadt-collection-' \
                                        'selections-of-photographs-p'
        response = self.client.get(url_collection)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"total_count": 1}')
        self.assertContains(response, '"next": null')
        self.assertContains(
            response,
            '"slug": "halberstadt-collection-selections-of-photographs-p"')

    def testCustomFacetInCollectionAPI(self):
        '''test that the custom facet shows up for a collection Resource'''
        url_collection = self.url_api + 'collection/5/?format=json'
        response = self.client.get(url_collection)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"custom_facet":')
        self.assertContains(response, 'contributor_ss')
        self.assertContains(response, 'collector')
        self.assertContains(response, 'coverage_ss')
        self.assertContains(response, 'Production')


class CollectionsViewTestCase(TestCase):
    '''Test the view function "collections" directly'''
    fixtures = ('collection.json', 'campus.json', 'repository.json')


class PublicViewTestCase(TestCase):
    '''Test the view for the public'''
    fixtures = ('collection.json', 'campus.json', 'repository.json')

    def testRootView(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/collection_list.html')
        self.assertContains(response, 'UC Berkeley')
        self.assertContains(response, 'collections')
        self.assertContains(
            response,
            '/189/a-is-for-atom-b-is-for-bomb-video-tape/')
        self.assertContains(response, '<form')
        self.assertContains(response, 'value="Search"')
        self.assertContains(response, '<input class="form-control mr-sm-2"'
            ' type="text"')

    def testSearchView(self):
        '''Test what happens when you search.
        Need to find good way to test paging with search
        '''
        response = self.client.get('/?q=aids')
        self.assertContains(response, '<tr>', count=2)
        response = self.client.get('/?q=born+digital')
        self.assertContains(response, '<tr>', count=5)
        self.assertContains(response, 'Watson')
        response = self.client.get('/?q=^born+digital')
        # no results
        self.assertNotContains(response, '<tr>')
        self.assertContains(response,
                            "No collections found for query: ^born dig")
        response = self.client.get('/?q=^bulletin')
        self.assertContains(response, '<tr>', count=3)
        response = self.client.get('/?q=ark%3A%2F13030%2Fkt5h4nf5dx')
        self.assertContains(response, '<tr>', count=1)
        self.assertContains(response, 'University Archives')
        response = self.client.get('/?q==Bulletin')
        self.assertNotContains(response, '<tr>')
        response = self.client.get(
            '/?q==Bulletin of Calif. division of Mines and Geology')
        self.assertContains(response, '<tr>', count=1)
        response = self.client.get('/?q=^Calif')
        self.assertContains(response, '<tr>', count=3)
        response = self.client.get('/?q=Calif')
        self.assertContains(response, '<tr>', count=16)

    def testUCBCollectionView(self):
        response = self.client.get('/UCB/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'collections')
        self.assertNotContains(
            response,
            '/21/w-gearhardt-photographs-photographs-of-newport-bea/">'
            'W. Gearhardt photographs'
        )
        self.assertContains(
            response,
            '/150/wieslander-vegetation-type-maps-photographs-in-192/')

    def testRepositoriesView(self):
        response = self.client.get('/repositories/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertContains(response, 'Mandeville')

    def testUCBRepositoriesView(self):
        response = self.client.get('/UCB/repositories/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertNotContains(response, 'Mandeville')
        self.assertContains(response, 'Bancroft Library')

    def testNOTUCCollectionView(self):
        response = self.client.get('/UC-/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<tr>', count=1)

    def testCollectionPublicView(self):
        '''Test view of one collection'''
        response = self.client.get(
            '/2/halberstadt-collection-selections-of-photographs-p/')
        self.assertContains(response, 'Halberstadt Collection')
        self.assertContains(response, 'Campus')
        self.assertContains(response, 'Davis')

    def testCollectionListViewPagination(self):
        '''Check the pagination of the collections view.
        This view is the "Root" view as well.
        Adding the OAC collections makes some sort of pagination needed
        here.'''
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/collection_list.html')
        self.assertContains(response, '<tr>', count=25)
        self.assertContains(response, 'class="pagination"')
        self.assertContains(
            response,
            '<li class="page-item disabled"><a class="page-link"' 
            'href="?page=1" title="First Page">&laquo;&laquo;</a></li>', 
            html=True
        )
        self.assertContains(
            response,
            '<li class="page-item"><a class="page-link" href="?page=8"' 
            'title="Next Group">&raquo;</a></li>',
            html=True)
        self.assertContains(
            response,
            '<li class="page-item active"><a class="page-link" href="#">1</a></li>',
            html=True
        )
        self.assertContains(response, 'page=8')
        response = self.client.get('/?page=8')
        self.assertContains(
            response,
            '<li class="page-item"><a class="page-link" href="?page=1" '
            'title="Previous Group">&laquo;</a></li>',
            html=True)
        self.assertContains(
            response,
            '<li class="page-item disabled"><a class="page-link" href="?page=8" '
            'title="Next Group">&raquo;</a></li>',
            html=True
        )
        self.assertContains(
            response,
            '<li class="page-item active"><a class="page-link" href="#">8</a></li>',
            html=True
        )
        response = self.client.get('/?page=3')
        self.assertContains(
            response,
            '<li class="page-item"><a class="page-link" href="?page=1" '
            'title="Previous Group">&laquo;</a></li>',
            html=True)
        self.assertContains(
            response,
            '<li class="page-item"><a class="page-link" href="?page=8" '
            'title="Next Group">&raquo;</a></li>',
            html=True)
        self.assertContains(
            response,
            '<li class="page-item active"><a class="page-link" href="#">3</a></li>',
            html=True
        )
        self.assertContains(response, '?page=5')
        self.assertContains(response, '?page=6')
        self.assertContains(response, '?page=1')
        response = self.client.get('/?page=3000')
        self.assertContains(
            response,
            '<li class="page-item"><a class="page-link" href="?page=1" '
            'title="Previous Group">&laquo;</a></li>',
            html=True)
        self.assertContains(
            response,
            '<li class="page-item disabled"><a class="page-link" href="?page=8" '
            'title="Next Group">&raquo;</a></li>',
            html=True
        )
        self.assertContains(
            response,
            '<li class="page-item active"><a class="page-link" href="#">8</a></li>',
            html=True
        )


class CampusTestCase(TestCase):
    fixtures = ('campus.json', )

    def testCampusSlugStartsWithUC(self):
        c = Campus()
        c.name = 'test'
        c.slug = 'test'
        self.assertRaises(ValueError, c.save)
        c.slug = 'UCtest'
        c.save()
        self.assertTrue(hasattr(c, 'ark'))
        self.assertTrue(hasattr(c, 'google_analytics_tracking_code'))

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
        except ValueError as e:
            self.assertEqual(e.args, (
                'Campus with ark ark:/13030/tf0p3009mq already exists', ))
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
    fixtures = ('collection.json', 'campus.json', 'repository.json')

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
        self.assertTemplateUsed(response,
                                'library_collection/collection_list.html')
        self.assertContains(response, 'UC Berkeley')
        # self.assertContains(response, 'New Test Campus')
        self.assertContains(response, 'collections')
        self.assertContains(
            response,
            "/5/1937-yolo-county-aerial-photographs-this-collectio/")


class EditViewTestCase(TestCase):
    '''Test the view for the public'''
    fixtures = ('collection.json', 'campus.json', 'repository.json',
                'user.json')
    current_app = 'edit'

    def setUp(self):
        self.http_auth = 'basic ' + b64encode('test_user:test_user'.encode()).decode()

        # self.http_auth = 'basic ' + 'test_user:test_user'.encode('base64')


    def testRootView(self):
        url = reverse('edit_collections')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/collection_list.html')
        self.assertContains(response, 'a-is-for')
        self.assertContains(response, '189 Collections')
        self.assertContains(
            response, EditViewTestCase.current_app +
            '/5/1937-yolo-county-aerial-photographs-this-collectio/')

    def testUCBCollectionView(self):
        url = reverse('edit_collections', kwargs={'campus_slug': 'UCB', })
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'Collections')
        self.assertContains(
            response, EditViewTestCase.current_app +
            '/150/wieslander-vegetation-type-maps-photographs-in-192/')

    def testRepositoriesView(self):
        url = reverse('edit_repositories')
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertContains(response, 'Mandeville')
        self.assertContains(response, '/edit/UCB')
        self.assertContains(response, '/edit/')

    def testUCBRepositoriesView(self):
        url = reverse('edit_repositories', kwargs={'campus_slug': 'UCB', })
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertNotContains(response, 'Mandeville')
        self.assertContains(response, 'Bancroft Library')
        url_edit_base = reverse('edit_collections')
        self.assertContains(response, url_edit_base)
        self.assertContains(response, url_edit_base + 'UCB')

    def testCollectionView(self):
        '''Test view of one collection'''
        url = reverse(
            'edit_detail',
            kwargs={
                'colid': 2,
                'col_slug':
                'halberstadt-collection-selections-of-photographs-p'
            }, )
        response = self.client.get(url, HTTP_AUTHORIZATION=self.http_auth)
        self.assertContains(response, 'Halberstadt Collection')
        self.assertContains(response, 'Campus')
        self.assertContains(response, 'Davis')
        self.assertNotContains(response, 'Bancroft Library')

    def testCollectionViewForm(self):
        '''Test form for modifying a collection'''
        url = reverse(
            'edit_detail',
            kwargs={
                'colid': 2,
                'col_slug':
                'halberstadt-collection-selections-of-photographs-p'
            }, )
        response = self.client.post(
            url, {'edit': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'Save')

    def testCollectionViewFormSubmission(self):
        '''Test form submission to modify a collection'''
        url = reverse(
            'edit_detail',
            kwargs={
                'colid': 2,
                'col_slug':
                'halberstadt-collection-selections-of-photographs-p'
            }, )
        response = self.client.post(
            url, {
                'appendix': 'A',
                'repositories': '9',
                'name': 'Halberstadt Collection',
                'campuses': ['1', '2']
            },
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/collection.html')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Davis')
        # can't modify campus or repo anymore
        self.assertNotContains(response, 'Bancroft')
        self.assertNotContains(response, 'Berkeley')
        response = self.client.post(
            url, {
                'appendix': 'A',
                'repositories': '9',
                'name': 'Halberstadt Collection',
                'campuses': ['1', '2'],
                'description': 'test description',
                'local_id': 'test local id',
                'url_local': 'http://example.edu'
            },
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertContains(response, 'test description')
        self.assertContains(response, 'test local id')
        self.assertContains(response, 'http://example.edu')

    def testCollectionViewFormSubmissionEmptyForm(self):
        '''Test form submission to modify a collection with an empty form'''
        url = reverse(
            'edit_detail',
            kwargs={
                'colid': 2,
                'col_slug':
                'halberstadt-collection-selections-of-photographs-p'
            }, )
        response = self.client.post(
            url, {'name': ''}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'Error:')
        self.assertContains(response, 'Please enter a')

    def testCollectionCreateViewForm(self):
        '''Test form to create a new collection'''
        url = reverse('edit_collections')
        response = self.client.post(
            url, {'new': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'Save')

    def testCollectionCreateViewFormSubmission(self):
        '''Test form submission to create a collection'''
        url = reverse('edit_collections')
        response = self.client.post(
            url, {
                'appendix': 'B',
                'repositories': '3',
                'name': 'new collection test',
                'campuses': ['1', '3'],
                'description': 'test description',
                'local_id': 'LOCID',
                'url_local': 'http://LOCURL.edu',
                'url_oac': 'http://OACURL.edu',
            },
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response, 'library_collection/collection.html')
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'new collection test')
        self.assertContains(response, 'Berkeley')
        self.assertContains(response, 'test description')
        self.assertContains(response, 'Internet Archive')
        self.assertContains(response, 'LOCID')
        self.assertContains(response, 'LOCURL')
        self.assertContains(response, 'OACURL')

    def testCollectionCreateViewFormSubmissionInvalid(self):
        '''Test form submission to create a collection'''
        url = reverse('edit_collections')
        response = self.client.post(
            url, {'appendix': 'B',
                  'name': 'new collection 2'},
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'new collection')
        self.assertContains(response, 'at least one campus')
        response = self.client.post(
            url, {
                'appendix': 'B',
                'name': 'new collection 2',
                'campuses': ['1', '3']
            },
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'new collection')
        self.assertContains(response, 'at least one unit')

    def testCollectionCreateViewFormSubmissionEmptyForm(self):
        '''Test form submission to create an empty collection'''
        url = reverse('edit_collections')
        response = self.client.post(
            url, {'name': ''}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/collection_edit.html')
        self.assertContains(response, 'Error:')

    def testRepositoryCreateViewForm(self):
        '''Test form to create a new repository'''
        url = reverse('edit_repositories')
        response = self.client.post(
            url, {'edit': 'true'}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertContains(response, 'Save')

    def testRepositoryCreateViewFormSubmission(self):
        '''Test form submission to create a repository'''
        url = reverse('edit_repositories')
        response = self.client.post(
            url, {'name': 'new repository',
                  'campuses': ['1', '4']},
            HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertContains(response, 'Add')
        self.assertContains(response, 'new repository')

        needle = '''<td><a href="/repository/11/new-repository/">new repository</a>
            <small class="muted">UC Berkeley UC Merced</small></td>'''
        self.assertInHTML(needle, response.content.decode('utf-8'))

    def testRepositoryCreateViewFormSubmissionEmptyForm(self):
        '''Test form submission to create an empty repository'''
        url = reverse('edit_repositories')
        response = self.client.post(
            url, {'name': ''}, HTTP_AUTHORIZATION=self.http_auth)
        self.assertTemplateUsed(response,
                                'library_collection/repository_list.html')
        self.assertContains(response, 'Error:')
        self.assertContains(response, 'Please enter a unit title')


class SyncWithOACTestCase(TestCase):
    '''Test sync with OAC repositories and EAD finding aid collections
    '''
    fixtures = ('collection.json', 'campus.json', 'repository.json',
                'user.json', 'group.json')

    def setUp(self):
        # need full path to fixtures dir to work with urllib file: schema
        self.dir_fixtures = os.path.join(FILE_DIR, 'fixtures')
        self.url_fixtures = 'file://localhost' + self.dir_fixtures + '/'

    def testSyncRepositories(self):
        '''See that the data updates. Use local test file in fixtures dir
        '''
        repos = Repository.objects.all()
        self.assertEqual(10, len(repos))
        n, n_up, n_new = sync_oac_repositories.main(
            url_oac_repo_list=self.url_fixtures + 'repository_OAC.json')
        self.assertEqual(124, n)
        self.assertEqual(0, n_up)
        self.assertEqual(120, n_new)
        repos = Repository.objects.all()
        self.assertEqual(130, len(repos))
        r = repos[100]
        r.name = 'bogus'
        r.save()
        n, n_up, n_new = sync_oac_repositories.main(
            url_oac_repo_list=self.url_fixtures + 'repository_OAC.json')
        self.assertEqual(124, n)
        self.assertEqual(1, n_up)
        self.assertEqual(0, n_new)
        repos = Repository.objects.all()
        self.assertEqual(130, len(repos))

    def testSyncCollections(self):
        '''See that the data updates. Use local test file in fixtures dir
        TODO: edge cases?
        '''
        colls = Collection.objects.all()
        self.assertEqual(189, len(colls))
        c = Collection.objects.get(
            url_oac='http://www.oac.cdlib.org/findaid/ark:/13030/kt5h4nf5dx/')
        self.assertEqual('X', c.harvest_type)
        self.assertEqual('', c.url_harvest)
        n, n_up, n_new, prefix_totals = sync_oac_collections.main(
            title_prefixes=['a', ], url_github_raw_base=self.url_fixtures)
        self.assertEqual(25, n)
        self.assertEqual(2, n_up)
        self.assertEqual(23, n_new)
        c = Collection.objects.get(
            url_oac='http://www.oac.cdlib.org/findaid/ark:/13030/kt5h4nf5dx/')
        self.assertEqual('OAC', c.harvest_type)
        self.assertEqual(
            'http://dsc.cdlib.org/search?facet=type-tab&style=cui&raw=1&'
            'relation=ark:/13030/kt5h4nf5dx',
            c.url_harvest)
        self.assertIn('/select-oac-id,\n/dpla_mapper?mapper_type=oac_dc',
                      c.enrichments_item)
        colls = Collection.objects.all()
        self.assertEqual(212, len(colls))
        n, n_up, n_new, prefix_totals = sync_oac_collections.main(
            title_prefixes=['a', ], url_github_raw_base=self.url_fixtures)
        self.assertEqual(25, n)
        self.assertEqual(25, n_up)
        self.assertEqual(0, n_new)
        colls = Collection.objects.all()
        self.assertEqual(212, len(colls))
        c = Collection.objects.get(
            url_oac='http://www.oac.cdlib.org/findaid/ark:/13030/kt5199r1g0')
        self.assertEqual(1, c.campus.count())
        self.assertEqual(1, c.campus.all()[0].id)
        self.assertEqual('X', c.harvest_type)
        c = Collection.objects.get(
            url_oac='http://www.oac.cdlib.org/findaid/ark:/13030/c8q52r3z')
        self.assertEqual(0, c.campus.count())
        self.assertEqual('OAC', c.harvest_type)
        self.assertEqual(
            'http://dsc.cdlib.org/search?facet=type-tab&style=cui&raw=1&'
            'relation=ark:/13030/c8q52r3z',
            c.url_harvest)
        self.assertEqual('X', c.dcmi_type)


class NewUserTestCase(TestCase):
    '''Test the response chain when a new user enters the system.
    With the HttpAuthMockMiddleware, a new user should be authenticated,
    created in the DB and then redirected to the new user message page.
    '''
    # TODO: check workflow for post verification
    fixtures = ('collection.json', 'campus.json', 'repository.json',
                'user.json', 'group.json')

    def testNewUserAuth(self):
        # http_auth = 'basic ' + 'bogus_new_user:bogus_new_user'.encode('base64')
        http_auth = 'basic ' + b64encode('bogus_new_user:bogus_new_user'.encode()).decode()

        url = reverse('edit_collections')
        response = self.client.get(url, HTTP_AUTHORIZATION=http_auth)
        self.assertTemplateUsed(
            response, 'library_collection/verification_required.html')
        # self.assertEqual(response.status_code, 200)
        # TODO: Test that the new user message page is presented to new user
        # check correct template and view????

# Copyright © 2016, Regents of the University of California
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the University of California nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
