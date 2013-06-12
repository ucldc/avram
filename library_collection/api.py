from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from library_collection.models import ProvenancialCollection, Campus

class CampusResource(ModelResource):
    class Meta:
        queryset = Campus.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        excludes = ['id']

class ProvenancialCollectionResource(ModelResource):
    campus = fields.ToManyField(CampusResource, 'campus', full=True)
    appendix = fields.CharField(attribute='get_appendix_display')

    class Meta:
        queryset = ProvenancialCollection.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        excludes = ['id']
