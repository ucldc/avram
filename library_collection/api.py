from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from library_collection.models import Collection, Campus, Repository
from library_collection.models import CollectionCustomFacet
from tastypie.constants import ALL, ALL_WITH_RELATIONS


class CampusResource(ModelResource):
    class Meta:
        queryset = Campus.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()


class RepositoryResource(ModelResource):
    campus = fields.ToManyField(CampusResource, 'campus', full=True)
    class Meta:
        queryset = Repository.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()


class CollectionResource(ModelResource):
    campus = fields.ToManyField(CampusResource, 'campus', full=True)
    repository = fields.ToManyField(RepositoryResource, 'repository', full=True)
    custom_facet = fields.OneToManyField('library_collection.api.CustomFacetResource',
            'collectioncustomfacet_set', full=True)

    class Meta:
        queryset = Collection.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'plist'])
        filtering = {
                "url_harvest": ('exact', 'startswith'),
                "slug": ALL,
                "harvest_type": ('exact'),
        }


class RikoltiCollectionResource(CollectionResource):
    # these API fields are used by rikolti's mapper component
    rikolti__pre_mapping = fields.ListField(attribute='pre_mapper_enrichments', null=True)
    rikolti__mapper_type = fields.CharField(attribute='rikolti_mapper_type', null=True)
    rikolti__enrichments = fields.ListField(attribute='self_enrichments', null=True)

    class Meta:
        queryset = Collection.published.all()
        filtering = {
            "harvest_type": ('exact'),
        }
        excludes = [
            'custom_facet',
            'date_last_harvested',
            'description',
            'disqus_shortname_prod',
            'disqus_shortname_test',
            'featured',
            'files_in_dams',
            'files_in_hand',
            'harvest_frequency',
            'merritt_extra_data',
            'merritt_id',
            'metadata_in_dams',
            'qa_completed',
            'extent',
            'dcmi_type',
            'harvest_exception_notes'
        ]


class RikoltiFetcherResource(CollectionResource):
    fetcher_registration = {
        'X': 'None',
        'OAC': 'oac',
        'OAI': 'oai',
        'SLR': 'solr',
        'MRC': 'marc',
        'NUX': 'nuxeo',
        'ALX': 'aleph',
        'SFX': 'ucsf_xml',
        'UCB': 'ucb_solr',
        'PRE': 'preservica_atom',
        'FLK': 'flickr',
        'YTB': 'youtube',
        'XML': 'xml_file',
        'EMS': 'emuseum',
        'UCD': 'ucd_json',
        'IAR': 'internet_archive',
        'PRA': 'preservica_api'
    }

    class Meta:
        queryset = Collection.objects.all()
        list_allowed_methods = ['get']
        filtering = {
            "harvest_type": ('exact'),
            "id": ('in'),
            "harvest_extra_data": ('isnull'),
            "ready_for_publication": ('isnull'),
            "solr_count": ('gt', 'lt'),
        }
        excludes = [
            'campus',
            'custom_facet',
            'date_last_harvested',
            'description',
            'disqus_shortname_prod',
            'disqus_shortname_test',
            'featured',
            'files_in_dams',
            'files_in_hand',
            'harvest_frequency',
            'merritt_extra_data',
            'merritt_id',
            'metadata_in_dams',
            'qa_completed',
            'extent',
            'dcmi_type',
            'harvest_exception_notes',
            'enrichments_item',
            'hosted',
            'local_id',
            'name',
            'repository',
            'rights_statement',
            'rights_status',
            'slug',
            'staging_notes',
            'url_local',
            'url_oac',
            'solr_count',
            'solr_last_updated',
            'mapper_type',
        ]

    def dehydrate_harvest_type(self, bundle):
        return self.fetcher_registration.get(bundle.data['harvest_type'])

    def dehydrate(self, bundle):
        bundle.data['collection_id'] = bundle.data['id']
        bundle.data.pop('id')
        bundle.data['harvest_data'] = {
            'url': bundle.data['url_harvest'],
            'harvest_extra_data': bundle.data['harvest_extra_data']
        }
        bundle.data.pop('url_harvest')
        bundle.data.pop('harvest_extra_data')
        return bundle


class CustomFacetResource(ModelResource):
    def __init__(self, *args, **kwargs):
        super(CustomFacetResource, self).__init__(*args, **kwargs)
        del self.fields['resource_uri']

    class Meta:
        queryset = CollectionCustomFacet.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        resource_name = 'custom_facet'
