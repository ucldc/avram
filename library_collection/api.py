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
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])
        filtering = {
                "url_harvest": ('exact', 'startswith'),
                "slug": ALL,
        }


class CustomFacetResource(ModelResource):
    def __init__(self, *args, **kwargs):
        super(CustomFacetResource, self).__init__(*args, **kwargs)
        del self.fields['resource_uri']

    class Meta:
        queryset = CollectionCustomFacet.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        resource_name = 'custom_facet'
