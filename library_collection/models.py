# models.py

from django.db import models
from django_extensions.db.fields import AutoSlugField
from human_to_bytes import bytes2human


class Campus(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=4)
    class Meta:
        verbose_name_plural = "campuses"
    def __unicode__(self):
        return self.name
    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.UC', [str(self.slug)])

class Status(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "statuses"
    def __unicode__(self):
        return self.name

class Restriction(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

class Need(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

class Collection(models.Model):
    DAMNS = 'D'
    OAI = 'O'
    CRAWL = 'C'
    PENDING = 'P'
    name = models.CharField(max_length=255)
    # uuid_field = UUIDField(primary_key=True)
    slug = AutoSlugField(max_length=50, populate_from=('name','description'), editable=True)
    collection_type = models.CharField(max_length=1, choices=(('A', 'Archival'), ('C', 'Curated')))
    campus = models.ManyToManyField(Campus)	# why not a multi-campus collection?
    repository = models.ManyToManyField('Repository', null=True, blank=True)
    description = models.TextField(blank=True)
    url_local = models.URLField(max_length=255,blank=True)
    url_oac = models.URLField(max_length=255,blank=True)
    url_was = models.URLField(max_length=255,blank=True)
    url_oai = models.URLField(max_length=255,blank=True)
    hosted = models.CharField(max_length=255,blank=True)
    status = models.ForeignKey(Status, null=True, blank=True, default = None)
    extent = models.BigIntegerField(blank=True, null=True, help_text="must be entered in bytes, will take abbreviations later")
    access_restrictions = models.ForeignKey(Restriction, null=True, blank=True, default = None)
    metadata_level = models.CharField(max_length=255,blank=True)
    metadata_standard = models.CharField(max_length=255,blank=True)
    need_for_dams = models.ForeignKey(Need, null=True, blank=True, default = None)
    oai_set_spec = models.CharField(max_length=255, blank=True)
    appendix = models.CharField(max_length=1, choices=( ('A', 'Nuxeo DAMS'), ('B', 'Harvest/Crawl')) )
    phase_one = models.BooleanField()

    @property
    def url(self):
        return self.url_local;

    @property
    def human_extent(self):
        return bytes2human(self.extent,format=u'%(value).1f\xa0%(symbol)s')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.details', [self.id, str(self.slug)])

class Repository(models.Model):
    '''Representation of a holding "repository" for UCLDC'''
    name = models.CharField(max_length=255)
    campus = models.ManyToManyField(Campus, null=True, blank=True)

    class Meta:
        verbose_name_plural = "repositories"
    def __unicode__(self):
        return self.name
