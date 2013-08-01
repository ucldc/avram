# sitemap.py

from django.contrib.sitemaps import Sitemap
from library_collection.models import Collection

class RegistrySitemap(Sitemap):
    priority = 0.5

    def items(self):
        # return Entry.objects.filter(is_draft=False)
        return Collection.objects.all()

    #def lastmod(self, obj):
        #return obj.pub_date

    # changefreq can be callable too
    #def changefreq(self, obj):
    #    return "daily" if obj.comments_open() else "never"

