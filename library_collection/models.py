# -*- coding: utf-8 -*-
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.urls import reverse
from human_to_bytes import bytes2human
from django.core.exceptions import ObjectDoesNotExist


class Campus(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=4)
    position = models.IntegerField(default=0)
    ark = models.CharField(max_length=255, blank=True)
    google_analytics_tracking_code = models.CharField(
        max_length=64,
        blank=True,
        help_text='Enable tracking of your digital assets hosted in the '
        'UCLDC by entering your Google Analytics tracking code.'
    )

    class Meta:
        verbose_name_plural = 'campuses'

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
            raise ValueError(
                'Campus slug must currently start with UC. Causes problem '
                'with reverse lookups if not currently'
            )
        if self.ark:  # not blank
            try:
                Campus.objects.get(ark=self.ark)
                raise ValueError('Campus with ark ' + self.ark +
                                 ' already exists')
            except ObjectDoesNotExist:
                pass
        return super(Campus, self).save(*args, **kwargs)


class Format(models.Model):
    '''File formats of data for input to DAMS.'''
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class CollectionCustomFacet(models.Model):
    '''This model is designed to allow a collection owner to select one of
    our Solr string values as a custom facet. Need to do as a separate model
    to allow list of these with custom labels
    To make serializing to TastyPie a lot easier, I'm using the full facet
    field as the 'code' for the choice. A bit space inefficient, but this table
    will never be huge.
    '''
    facet_choices = (
        ('contributor_ss', 'contributor'), ('coverage_ss', 'coverage'),
        ('creator_ss', 'creator'), ('date_ss', 'date'),
        ('extent_ss', 'extent'), ('format_ss', 'format'),
        ('genre_ss', 'genre'), ('language_ss', 'language'),
        ('location_ss', 'location'), ('publisher_ss', 'publisher'),
        ('relation_ss', 'relation'), ('rights_ss', 'rights'),
        ('rights_holder_ss', 'rights_holder'),
        ('rights_note_ss', 'rights_note'), ('rights_date_ss', 'rights_date'),
        ('source_ss', 'source'), ('subject_ss', 'subject'),
        ('temporal_ss', 'temporal'))
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE)
    facet_field = models.CharField(max_length=20, choices=facet_choices)
    label = models.CharField(max_length=255)


class Collection(models.Model):
    DAMNS = 'D'
    OAI = 'O'
    CRAWL = 'C'
    PENDING = 'P'
    name = models.CharField(max_length=255, verbose_name='Collection Title')
    # uuid_field = UUIDField(primary_key=True)
    slug = AutoSlugField(
        max_length=50, populate_from=('name', 'description'), editable=True)
    campus = models.ManyToManyField(Campus, blank=True)
    repository = models.ManyToManyField(
        'Repository', blank=True, verbose_name='Unit')
    description = models.TextField(blank=True)
    local_id = models.CharField(
        max_length=1028,
        blank=True,
        help_text='used for google analytics subsetting')
    url_local = models.URLField(
        max_length=255, blank=True, help_text='Collection homepage URL')
    url_oac = models.URLField(
        max_length=255, blank=True, help_text='OAC finding aid URL')
    url_harvest = models.URLField(
        max_length=255, blank=True, verbose_name='Harvest Endpoint')
    hosted = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Existing metadata (Format/Output)',
        help_text='Indicate format and output')
    extent = models.BigIntegerField(
        blank=True,
        null=True,
        help_text='must be entered in bytes, will take abbreviations later')
    HARVEST_TYPE_CHOICES = (
        ('X', 'None'),
        ('OAC', 'Legacy OAC'),
        # ('OAJ', 'OAC json api'),
        ('OAI', 'OAI-PMH'),
        ('SLR', 'Solr Index'),
        ('MRC', 'MARC21'),
        ('NUX', 'Shared DAMS'),
        ('ALX', 'Aleph MARC XML'),
        ('SFX', 'UCSF XML Search Results (tobacco)'),
        ('UCB', 'Solr Generic - cursorMark'),
        ('PRE', 'Preservica CMIS Atom Feed'),
        ('FLK', 'Flickr Api All Public Photos'),
        ('YTB', 'YouTube Api - Playlist Videos'),
        ('XML', 'XML File'),
        ('EMS', 'eMuseum API'),
        ('UCD', 'UC Davis JSON'),
        )
    harvest_type = models.CharField(
        max_length=3, choices=HARVEST_TYPE_CHOICES, default='X')
    harvest_extra_data = models.CharField(
        max_length=511,
        blank=True,
        help_text='extra text data needed for the particular type of harvest.')
    enrichments_item = models.TextField(
        blank=True,
        help_text='Enhancement chain to run on individual harvested items.')
    formats = models.ManyToManyField(
        Format, blank=True, help_text='File formats for DAMS ingest')
    staging_notes = models.TextField(
        blank=True,
        default='',
        help_text='Possible support needed by contributor')
    files_in_hand = models.BooleanField(default=False)
    files_in_dams = models.BooleanField(default=False)
    metadata_in_dams = models.BooleanField(default=False)
    qa_completed = models.BooleanField(default=False)
    ready_for_publication = models.BooleanField(default=False)
    featured = models.BooleanField(
        default=False, help_text='Collection featured on repository home page')
    RIGHTS_CHOICES = (('CR', 'copyrighted'), ('PD', 'public domain'),
                      ('UN', 'copyright unknown'), ('X', '-----'))
    rights_status = models.CharField(
        max_length=3, choices=RIGHTS_CHOICES, default='X')
    rights_statement = models.TextField(blank=True)
    DCMI_TYPES = (
        ('C', 'Collection'),
        ('D', 'Dataset'),
        ('E', 'Event'),
        ('I', 'Image'),
        ('R', 'Interactive Resource'),
        ('F', 'Moving Image'),
        ('V', 'Service'),
        ('S', 'Software'),
        ('A', 'Sound'),  # A for audio
        ('T', 'Text'),
        ('P', 'Physical Object'),
        ('X', '-----')  # default, not set
    )
    dcmi_type = models.CharField(
        max_length=1,
        choices=DCMI_TYPES,
        default='X',
        help_text='DCMI Type for objects in this collection')
    date_last_harvested = models.DateField(null=True, blank=True)
    harvest_frequency = models.DurationField(null=True, blank=True)
    harvest_exception_notes = models.TextField(
        blank=True,
        help_text='Notes on processing quirks')
    merritt_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Merritt Id (ARK)')
    merritt_extra_data = models.CharField(
        max_length=511,
        blank=True,
        help_text='nuxeo path for Merritt harvest (usually the same as Harvest extra data)')
    disqus_shortname_prod = models.CharField(
        max_length=64,
        blank=True,
        help_text='put disqus on production with this shortcode (from disqus admin)')
    disqus_shortname_test = models.CharField(
        max_length=64,
        blank=True,
        help_text='put disqus on test with this shortcode')


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
        # if 'cdl-registry' in socket.gethostname() else socket.getfqdn()
        return 'registry.cdlib.org'

    @property
    def url_api(self):
        '''Return url for the tastypie api endpoint for this collection'''
        return ''.join(('https://', self._hostname, reverse(
            'api_dispatch_detail',
            kwargs={
                'resource_name': 'collection',
                'api_name': 'v1',
                'pk': self.id
            })))

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
        return bytes2human(self.extent, format=u'%(value).1f\xa0%(symbol)s')

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
        self.name = self.name.strip()
        if len(self.name) > 255:
            self.name = self.name[:255]
        return super(Collection, self).save(*args, **kwargs)


class Repository(models.Model):
    '''Representation of a holding "repository" for UCLDC'''
    name = models.CharField(max_length=255)
    campus = models.ManyToManyField(Campus, blank=True)
    slug = AutoSlugField(max_length=50, populate_from=('name'), editable=True)
    ark = models.CharField(max_length=255, blank=True)
    aeon_prod = models.CharField(max_length=255, blank=True)
    aeon_test = models.CharField(max_length=255, blank=True)
    google_analytics_tracking_code = models.CharField(
        max_length=64,
        blank=True,
        help_text='Enable tracking of your digital assets hosted in the '
        'UCLDC by entering your Google Analytics tracking code.'
    )

    class Meta:
        verbose_name_plural = 'repositories'

    def __unicode__(self):
        campuses = self.campus.all()
        if campuses:
            return u'{0} {1}'.format(campuses[0].slug, self.name)
        else:
            return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('library_collection.views.repository_collections',
                [self.id, str(self.slug)])

    def save(self, *args, **kwargs):
        '''Check no duplicate arks for repos that have them
        '''
        self.name = self.name.strip()
        if not self.id:  # new repo
            if self.ark:  # not blank
                try:
                    Repository.objects.get(ark=self.ark)
                    raise ValueError('Unit with ark ' + self.ark +
                                     ' already exists')
                except ObjectDoesNotExist:
                    pass
        return super(Repository, self).save(*args, **kwargs)

# Copyright © 2016, Regents of the University of California
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the University of California nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
