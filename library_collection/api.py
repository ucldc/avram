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


rikolti_filters = {
    "harvest_type": ('exact'),
    "id": ('in'),
    "harvest_extra_data": ('isnull'),
    "ready_for_publication": (ALL),
    "solr_count": ('gt', 'lt'),
    "enrichments_item": (ALL),
    "mapper_type": (ALL)
}

core_fields = [
    'name', 'description', 'featured', 'slug', 'campus', 'repository',
    'custom_facet'
]

harvest_fields = [ 
    # harvest fields
    'dcmi_type', 'rights_statement', 'rights_status', 'enrichments_item'
]

fetcher_fields = ['harvest_extra_data', 'url_harvest']

rikolti_excludes = [
    # disqus fields
    'disqus_shortname_prod', 'disqus_shortname_test',
    # defunct (?) fields
    'files_in_dams', 'files_in_hand', 'date_last_harvested',
    'harvest_frequency', 'metadata_in_dams', 'qa_completed', 'extent',
    'harvest_exception_notes', 'hosted', 'staging_notes',
    # merritt integration fields
    'merritt_extra_data', 'merritt_id',
    # not sure what these are
    'local_id', 'url_local', 'url_oac',
]

class RikoltiCollectionResource(CollectionResource):
    # these API fields are used by rikolti's mapper component
    rikolti__pre_mapping = fields.ListField(attribute='pre_mapper_enrichments', null=True)
    rikolti__mapper_type = fields.CharField(attribute='rikolti_mapper_type', null=True)
    rikolti__enrichments = fields.ListField(attribute='self_enrichments', null=True)

    class Meta:
        queryset = Collection.objects.all()
        list_allowed_methods = ['get']
        filtering = rikolti_filters
        excludes = rikolti_excludes


class RikoltiMapperResource(CollectionResource):
    class Meta:
        queryset = Collection.objects.all()
        list_allowed_methods = ['get']
        filtering = rikolti_filters
        excludes = rikolti_excludes + core_fields + harvest_fields + fetcher_fields

    def dehydrate(self, bundle):
        bundle.data['collection_id'] = bundle.data['id']
        bundle.data.pop('id')
        return bundle


class RikoltiFetcherResource(CollectionResource):
    rikolti_fetcher_registration = {
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
        filtering = rikolti_filters
        excludes = rikolti_excludes + core_fields + harvest_fields

    def dehydrate_harvest_type(self, bundle):
        return self.rikolti_fetcher_registration.get(bundle.data['harvest_type'])

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
