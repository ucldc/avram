from tastypie.resources import ModelResource
from library_collections.models import ProvenancialCollection

class ProvenancialCollectionResource(ModelResource):
    class Meta:
        queryset = ProvenancialCollection.objects.all()
