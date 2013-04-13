from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from library_collections.models import ProvenancialCollection

class ProvenancialCollectionResource(ModelResource):
    class Meta:
        queryset = ProvenancialCollection.objects.all()
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
