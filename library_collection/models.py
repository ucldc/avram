# models.py

import subprocess
import shlex
import os
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.core.urlresolvers import reverse
from human_to_bytes import bytes2human
from positions.fields import PositionField


class Campus(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=4)
    position = models.IntegerField(default=0)
    ark = models.CharField(max_length=255, blank=True) 
    class Meta:
        verbose_name_plural = "campuses"
    def __unicode__(self):
        return self.name
    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.UC', [str(self.slug)])

    def save(self, *args, **kwargs):
        '''Make sure the campus slug starts with UC, has implications in the 
        urls.py currently (2013-12-18)
        May want to change this in future
        '''
        if self.slug[:2] != 'UC':
            raise ValueError('Campus slug must currently start with UC. Causes problem with reverse lookups if not currently')
        return super(Campus, self).save(*args, **kwargs)


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
    harvest_script = os.environ.get('HARVEST_SCRIPT', os.environ['HOME'] + '/code/ucldc_harvester/start_harvest.bash')
    name = models.CharField(max_length=255)
    # uuid_field = UUIDField(primary_key=True)
    slug = AutoSlugField(max_length=50, populate_from=('name','description'), editable=True)
    collection_type = models.CharField(max_length=1, blank=True, choices=(('A', 'Archival'), ('C', 'Curated')))
    campus = models.ManyToManyField(Campus)	# why not a multi-campus collection?
    repository = models.ManyToManyField('Repository', null=True, blank=True)
    description = models.TextField(blank=True)
    url_local = models.URLField(max_length=255,blank=True)
    url_oac = models.URLField(max_length=255,blank=True)
    url_was = models.URLField(max_length=255,blank=True)
    url_oai = models.URLField(max_length=255,blank=True)
    url_harvest = models.URLField(max_length=255,blank=True)
    hosted = models.CharField(max_length=255,blank=True)
    status = models.ForeignKey(Status, null=True, blank=True, default = None)
    extent = models.BigIntegerField(blank=True, null=True, help_text="must be entered in bytes, will take abbreviations later")
    access_restrictions = models.ForeignKey(Restriction, null=True, blank=True, default = None)
    metadata_level = models.CharField(max_length=255,blank=True)
    metadata_standard = models.CharField(max_length=255,blank=True)
    need_for_dams = models.ForeignKey(Need, null=True, blank=True, default = None)
    HARVEST_TYPE_CHOICES = ( ('X', 'None'), ('OAC', 'OAC xml collection search'), ('OAJ', 'OAC json api'), ('OAI', 'OAI-PMH'))
    harvest_type = models.CharField(max_length=3, choices=HARVEST_TYPE_CHOICES, default='X')
    harvest_extra_data = models.CharField(max_length=511, blank=True, help_text="extra text data needed for the particular type of harvest.")
    APPENDIX_CHOICES = ( ('A', 'Nuxeo DAMS'), ('B', 'Harvest/Crawl'))
    appendix = models.CharField(max_length=1, choices=APPENDIX_CHOICES)
    phase_one = models.BooleanField()
    enrichments_item = models.TextField(blank=True, help_text="Enhancement chain to run on individual harvested items.")

    @property
    def url(self):
        return self.url_local;
    
    @property
    def url_api(self):
        '''Return url for the tastypie api endpoint for this collection'''
        return reverse('api_dispatch_detail', kwargs={'resource_name':'collection', 'api_name':'v1', 'pk':self.id}) 

    # This is a temporary property for the case of just 
    # giving some reference to actual content.
    # The url fields will get revisited next cycle.  
    @property
    def first_url(self):
        if self.url_local != '':
            return self.url_local
        elif self.url_oac != '':
            return self.url_oac
        elif self.url_was != '':
            return self.url_was
        else:
            return False

    @property
    def human_extent(self):
        return bytes2human(self.extent,format=u'%(value).1f\xa0%(symbol)s')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.details', [self.id, str(self.slug)])

    def start_harvest(self, user):
        '''Kick off the harvest.

        Harvest is asyncronous. Email is sent to site admin? annoucing the 
        start of a harvest for the collection.

        passes the user email and the uri for the tastypie data for the
        collection.
        '''
        #call is going to need : collection name, campus, repo, type of harvest, harvest url, harvest_extra_data (set spec, etc), request.user
        #TODO: support other harvests, rationalize the data
        if not self.url_harvest:
            raise TypeError('Not a harvestable collection - ' + self.name)
        cmd_line = ' '.join((self.harvest_script, user.email, self.url_api))
        p = subprocess.Popen(shlex.split(cmd_line))
        return p.pid


class Repository(models.Model):
    '''Representation of a holding "repository" for UCLDC'''
    name = models.CharField(max_length=255)
    campus = models.ManyToManyField(Campus, null=True, blank=True)
    slug = AutoSlugField(max_length=50, populate_from=('name'), editable=True)

    class Meta:
        verbose_name_plural = "repositories"
    def __unicode__(self):
        campuses = self.campus.all()
        if campuses:
            return u'{0} {1}'.format(campuses[0].slug, self.name)
        else:
            return self.name
