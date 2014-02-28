from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from library_collection.models import Collection, Campus, Repository

class CampusResource(ModelResource):
    class Meta:
        queryset = Campus.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        excludes = ['id']

class RepositoryResource(ModelResource):
    campus = fields.ToManyField(CampusResource, 'campus', full=True)
    class Meta:
        queryset = Repository.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        excludes = ['id']

class CollectionResource(ModelResource):
    campus = fields.ToManyField(CampusResource, 'campus', full=True)
    repository = fields.ToManyField(RepositoryResource, 'repository', full=True)
    appendix = fields.CharField(attribute='get_appendix_display')

    class Meta:
        queryset = Collection.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        excludes = ['id']
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])
