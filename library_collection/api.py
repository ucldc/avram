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
    rikolti__mapper_type = fields.CharField(attribute='mapper_type', null=True)
    rikolti__enrichments = fields.ListField(attribute='self_enrichments', null=True)


class CustomFacetResource(ModelResource):
    def __init__(self, *args, **kwargs):
        super(CustomFacetResource, self).__init__(*args, **kwargs)
        del self.fields['resource_uri']

    class Meta:
        queryset = CollectionCustomFacet.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        resource_name = 'custom_facet'
