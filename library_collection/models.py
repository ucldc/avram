# models.py

import subprocess
import shlex
import os
import socket
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.core.urlresolvers import reverse
from human_to_bytes import bytes2human
from positions.fields import PositionField
from  django.core.exceptions import ObjectDoesNotExist


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
        if self.ark: #not blank
            try:
                c = Campus.objects.get(ark=self.ark)
                raise ValueError("Campus with ark "+self.ark+" already exists")
            except ObjectDoesNotExist:
                pass
        return super(Campus, self).save(*args, **kwargs)

class Format(models.Model):
    '''File formats of data for input to DAMS.'''
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

class Collection(models.Model):
    DAMNS = 'D'
    OAI = 'O'
    CRAWL = 'C'
    PENDING = 'P'
    harvest_script = os.environ.get('HARVEST_SCRIPT', os.environ['HOME'] + '/code/harvester/start_harvest.bash')
    name = models.CharField(max_length=255, verbose_name='Collection Title')
    # uuid_field = UUIDField(primary_key=True)
    slug = AutoSlugField(max_length=50, populate_from=('name','description'), editable=True)
    campus = models.ManyToManyField(Campus, blank=True)
    repository = models.ManyToManyField('Repository', null=True, blank=True,
            verbose_name='Unit')
    description = models.TextField(blank=True)
    url_local = models.URLField(max_length=255,blank=True,
            help_text='Collection homepage URL')
    url_oac = models.URLField(max_length=255,blank=True,
            help_text='OAC finding aid URL')
    url_harvest = models.URLField(max_length=255,blank=True,
                   verbose_name='Harvest Endpoint')
    hosted = models.CharField(max_length=255,blank=True,
            verbose_name='Existing metadata (Format/Output)',
            help_text='Indicate format and output')
    extent = models.BigIntegerField(blank=True, null=True, help_text="must be entered in bytes, will take abbreviations later")
    HARVEST_TYPE_CHOICES = (
            ('X', 'None'),
            ('OAC', 'Legacy OAC'),
            ('OAJ', 'OAC json api'),
            ('OAI', 'OAI-PMH'),
            ('SLR', 'Solr Index'),
            ('MRC', 'MARC21'),
            ('NUX', 'Shared DAMS'),
            ('ALX', 'Aleph MARC XML'),
            ('SFX', 'UCSF XML Search Results (tobacco)'),
            ('TBD', 'Harvest type TBD'),
    )
    harvest_type = models.CharField(max_length=3, choices=HARVEST_TYPE_CHOICES, default='X')
    harvest_extra_data = models.CharField(max_length=511, blank=True, help_text="extra text data needed for the particular type of harvest.")
    enrichments_item = models.TextField(blank=True, help_text="Enhancement chain to run on individual harvested items.")
    formats = models.ManyToManyField(Format, null=True, blank=True,
            help_text='File formats for DAMS ingest')
    staging_notes = models.TextField(blank=True, default='',
            help_text='Possible support needed by contributor')
    files_in_hand = models.BooleanField()
    files_in_dams = models.BooleanField()
    metadata_in_dams = models.BooleanField()
    qa_completed = models.BooleanField()
    ready_for_publication = models.BooleanField(default=False)
    featured = models.BooleanField(default=False,
            help_text='Collection featured on repository home page')
    RIGHTS_CHOICES = (
            ('CR', 'copyrighted'),
            ('PD', 'public domain'),
            ('UN', 'copyright unknown'),
            ('X', '-----')
            )
    rights_status = models.CharField(max_length=3, choices=RIGHTS_CHOICES,
            default='X')
    rights_statement = models.TextField(blank=True)
    DCMI_TYPES = (
            ('C', 'Collection'),
            ('D', 'Dataset'),
            ('E', 'Event'),
            ('I', 'Image'),
            ('R', 'Interactive Resource'),
            ('V', 'Service'),
            ('S', 'Software'),
            ('A', 'Sound'), # A for audio
            ('T', 'Text'),
            ('X', '-----') # default, not set
            )
    dcmi_type = models.CharField(max_length=1, choices=DCMI_TYPES,
            default='X', help_text="DCMI Type for objects in this collection")

    @property
    def url(self):
        return self.url_local

    @property
    def courtesy(self):
        out = []
        for campus in self.campus.all():
            out.append(campus.name)
        if len(out) == 0:
            for repository in self.repository.all():
                out.append(repository.name)
        return out
    
    @property
    def _hostname(self):
        '''Because of the aliasing, hard to get actual external hostname in
        production environment. Works correctly in stage & dev.'''
        return 'registry.cdlib.org' if 'cdl-registry' in socket.gethostname() else socket.getfqdn()

    @property
    def url_api(self):
        '''Return url for the tastypie api endpoint for this collection'''
        return ''.join(('https://', self._hostname, reverse('api_dispatch_detail', kwargs={'resource_name':'collection', 'api_name':'v1', 'pk':self.id})))

    # This is a temporary property for the case of just 
    # giving some reference to actual content.
    # The url fields will get revisited next cycle.  
    @property
    def first_url(self):
        if self.url_local != '':
            return self.url_local
        elif self.url_oac != '':
            return self.url_oac
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

    def save(self, *args, **kwargs):
        ''' When running in mysql, names that are too long (there is one at
        http://www.oac.cdlib.org/findaid/ark:/13030/c8th8nj6) causes the 
        save to bomb. Going to truncate to 255 chars and throw out rest -
        MER 20140507
        '''
        if len(self.name) > 255:
            self.name = self.name[:255]
        return super(Collection, self).save(*args, **kwargs)

    def start_harvest(self, user):
        '''Kick off the harvest.

        Harvest is asyncronous. Email is sent to site admin? annoucing the 
        start of a harvest for the collection.

        passes the user email and the uri for the tastypie data for the
        collection.
        '''
        #call is going to need : collection name, campus, repo, type of harvest, harvest url, harvest_extra_data (set spec, etc), request.user
        #TODO: support other harvests, rationalize the data
        if self.harvest_type == 'X':
            raise TypeError('Not a harvestable collection - "{0}" ID:{1}. No harvest type specified.'.format(self.name, self.id))
        if not self.url_harvest:
            raise TypeError('Not a harvestable collection - "{0}" ID:{1}. No URL for harvest.'.format(self.name, self.id))
        cmd_line = ' '.join((self.harvest_script, user.email, self.url_api))
        p = subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        return p.pid


class Repository(models.Model):
    '''Representation of a holding "repository" for UCLDC'''
    name = models.CharField(max_length=255)
    campus = models.ManyToManyField(Campus, null=True, blank=True)
    slug = AutoSlugField(max_length=50, populate_from=('name'), editable=True)
    ark = models.CharField(max_length=255, blank=True) 

    class Meta:
        verbose_name_plural = "repositories"
    def __unicode__(self):
        campuses = self.campus.all()
        if campuses:
            return u'{0} {1}'.format(campuses[0].slug, self.name)
        else:
            return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.repository_collections', [self.id, str(self.slug)])

    def save(self, *args, **kwargs):
        '''Check no duplicate arks for repos that have them
        '''
        if not self.id: #new repo
            if self.ark: #not blank
                try:
                    c = Repository.objects.get(ark=self.ark)
                    raise ValueError("Unit with ark "+self.ark+" already exists")
                except ObjectDoesNotExist:
                    pass
        return super(Repository, self).save(*args, **kwargs)
