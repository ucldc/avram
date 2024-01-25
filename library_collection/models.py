# -*- coding: utf-8 -*-
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.urls import reverse
from .human_to_bytes import bytes2human
from django.core.exceptions import ObjectDoesNotExist
from collections import namedtuple


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

    def __str__(self):
        return self.name

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


# mapper types
# legacy keys, rikolti values
rikolti_mapper_type_conversion = {
    "dublin_core": None,
    "cavpp_islandora": None,
    "cca_vault_oai_dc": "oai.cca_vault",
    "chapman_oai_dc": "oai.chapman",
    "tv_academy_oai_dc": "oai.tv_academy",
    "ucsc_oai_dpla": "oai.samvera",
    "up_oai_dc": "oai.up",
    "yosemite_oai_dc": "oai.yosemite",
    "calpoly_oai_dc": None,
    "contentdm_oai_dc": "oai.content_dm.contentdm",
    "arck_oai": "oai.content_dm.arck",
    "black_gold_oai": "oai.content_dm.blackgold",
    "califa_oai_dc": None,
    "chico_oai_dc": "oai.content_dm.chico",
    "chula_vista_pl_contentdm_oai_dc": "oai.content_dm.cvpl",
    "contentdm_oai_dc_get_sound_thumbs": "oai.content_dm.pepperdine",
    "csu_sac_oai_dc": "oai.content_dm.csu_sac",
    "csudh_contentdm_oai_dc": "oai.content_dm.csudh",
    "lapl_oai": "oai.content_dm.lapl",
    "quartex_oai": "oai.quartex",
    "usc_oai_dc": None,
    "csu_dspace_mets": "oai.csu_dspace",
    "csuci_mets": "oai.csuci_mets",
    "islandora_oai_dc": "oai.islandora",
    "burbank_islandora": "oai.islandora.burbank",
    "caltech_restrict": "oai.islandora.caltech",
    "chs_islandora": "oai.islandora.chs",
    "sjsu_islandora": "oai.islandora",
    "lapl_26096": "lapl_26096.lapl_26096",
    "oac_dc": "oac.oac",
    "oac_dc_suppress_desc_2": "oac.suppress_description",
    "oac_dc_suppress_publisher": "oac.suppress_publisher",
    "omeka": "oai.omeka",
    "csa_omeka": "oai.omeka.csa",
    "omeka_nothumb": "oai.omeka.nothumb",
    "omeka_santa_clara": None,
    "pspl_oai_dc": "oai.pspl",
    "ucla_solr_dc": "ucla_solr.ucla_solr",
    "ucsd_blacklight_dc": "ucsd_blacklight.ucsd_blacklight",
    "preservica_api": "preservica.preservica",
    "cmis_atom": "cmis_atom.cmis_atom",
    "emuseum_xml": "emuseum_xml.emuseum_xml",
    "flickr_api": "flickr.flickr",
    "flickr_sdasm": "flickr.sdasm",
    "flickr_sppl": "flickr.sppl",
    "internet_archive": "internet_archive.internet_archive",
    "marc": "marc.marc",
    "csl_marc": "marc.csl",
    "sfpl_marc": None,
    "sierramadre_marc": "marc.sierra",
    "ucb_tind_marc": "marc.ucb_tind",
    "ucsb_aleph_marc": "marc.ucsb_aleph",
    "pastperfect_xml": "pastperfect_xml.pastperfect_xml",
    "sanjose_pastperfect": "pastperfect_xml.san_jose",
    "ucb_bampfa_solr": "ucb_bampfa.ucb_bampfa",
    "ucd_json": "ucd_json.ucd_json",
    "ucldc_nuxeo": "nuxeo.nuxeo",
    "ucldc_nuxeo_dc": "nuxeo.nuxeo",
    "ucsf_solr": "ucsf_solr.ucsf_solr",
    "youtube_video_snippet": "youtube.youtube",
}


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
    sort_by = models.CharField(max_length=20, choices=(
        ('count', 'number of results'),
        ('value', 'alphanumeric order')), default='count')


class PublishedCollectionManager(models.Manager):
    def get_queryset(self):
        return super(PublishedCollectionManager, self).get_queryset().exclude(
            ready_for_publication=False).exclude(enrichments_item__exact='')

FetchType = namedtuple("FetchType", "registry_code display_name rikolti_code")

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
        'Repository', verbose_name='Unit')
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
    HARVEST_TYPE_CHOICES = [
        FetchType('X', 'None', 'None'),
        FetchType('ETL', 'Rikolti ETL', 'calisphere_solr'),
        FetchType('OAC', 'Legacy OAC', 'oac'),
        # ('OAJ', 'OAC json api'),
        FetchType('OAI', 'OAI-PMH', 'oai'),
        FetchType('SLR', 'Solr Index', 'solr'),
        FetchType('MRC', 'MARC21', 'marc'),
        FetchType('NUX', 'Shared DAMS', 'nuxeo'),
        FetchType('ALX', 'Aleph MARC XML', 'aleph'),
        FetchType('SFX', 'UCSF XML Search Results (tobacco)', 'ucsf_xml'),
        FetchType('UCB', 'Solr Generic - cursorMark', 'ucb_solr'),
        FetchType('PRE', 'Preservica CMIS Atom Feed', 'preservica_atom'),
        FetchType('FLK', 'Flickr Api All Public Photos', 'flickr'),
        FetchType('YTB', 'YouTube Api - Playlist Videos', 'youtube'),
        FetchType('XML', 'XML File', 'xml_file'),
        FetchType('EMS', 'eMuseum API', 'emuseum'),
        FetchType('UCD', 'UC Davis JSON', 'ucd_json'),
        FetchType('IAR', 'Internet Archive API', 'internet_archive'),
        FetchType('PRA', 'Preservica API', 'preservica_api'),
    ]
    harvest_type_choices = [
        (fetch_type.registry_code, fetch_type.display_name)
        for fetch_type in HARVEST_TYPE_CHOICES
    ]
    harvest_type = models.CharField(
        max_length=3, choices=harvest_type_choices, default='X')
    harvest_extra_data = models.CharField(
        max_length=511,
        blank=True,
        help_text='extra text data needed for the particular type of harvest.')
    enrichments_item = models.TextField(
        blank=True,
        help_text='Enhancement chain to run on individual harvested items.')
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
    solr_count = models.IntegerField(
        default=0, help_text='Number of items in Solr index')
    solr_last_updated = models.DateTimeField(
        null=True, blank=True, help_text='Last time Solr count was updated')
    mapper_type = models.CharField(
        null=True, blank=True, max_length=511, help_text='Auto-Generated from Enrichments')
    rikolti_mapper_type = models.CharField(
        null=True, blank=True, max_length=511, help_text='Matches module name in Rikolti')
    metadata_density_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    metadata_density_score_last_updated = models.DateTimeField(
        null=True, blank=True, help_text='Last time metadata density score was updated')

    objects = models.Manager()
    published = PublishedCollectionManager()

    @property
    def enrichment_array(self):
        split_enrichments = self.enrichments_item.split(',\r\n')
        if len(split_enrichments[0]) > 255:
            split_enrichments = self.enrichments_item.split(',\n')
        if len(split_enrichments[0]) > 255:
            f"split failed: {self.id}"
            return None
        return split_enrichments

    @property
    def id_enrichment(self):
        if not self.enrichment_array:
            return None
        first_enrichment = self.enrichment_array[0]
        if first_enrichment.startswith('/dpla_mapper'):
            return None
        return first_enrichment

    @property
    def legacy_mapper_type(self):
        if not self.enrichment_array:
            return None
        mapper_enrichment = None
        for enrichment in self.enrichment_array:
            if enrichment.startswith('/dpla_mapper'):
                mapper_enrichment = enrichment.split('=')[1]
                break
        return mapper_enrichment

    @property
    def pre_mapper_enrichments(self):
        if self.harvest_type == 'ETL':
            return None
        if not self.mapper_type:
            print(f"no mapper type: {self.id}")
            return None
        mapper_index = self.enrichment_array.index(
            f"/dpla_mapper?mapper_type={self.legacy_mapper_type}")
        return self.enrichment_array[:mapper_index]

    @property
    def self_enrichments(self):
        if self.harvest_type == 'ETL':
            return None
        if not self.legacy_mapper_type:
            print(f"no mapper type: {self.id}")
            return None
        mapper_index = self.enrichment_array.index(
            f"/dpla_mapper?mapper_type={self.legacy_mapper_type}")
        if mapper_index not in [0,1]:
            print(f"too many items before mapper: {self.enrichment_array[:mapper_index+1]}")
        return self.enrichment_array[mapper_index+1:]

    def index_of_enrichment(self, enrichment):
        if not self.enrichment_array:
            return None
        if enrichment in self.enrichment_array:
            return self.enrichment_array.index(enrichment)
        else:
            return -1

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


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail',
            kwargs={'colid': self.id, 'col_slug': str(self.slug)})

    def save(self, *args, **kwargs):
        ''' When running in mysql, names that are too long (there is one at
        http://www.oac.cdlib.org/findaid/ark:/13030/c8th8nj6) causes the
        save to bomb. Going to truncate to 255 chars and throw out rest -
        MER 20140507
        '''
        self.name = self.name.strip()
        if len(self.name) > 255:
            self.name = self.name[:255]
        self.mapper_type = self.legacy_mapper_type
        if self.harvest_type == 'ETL':
            self.rikolti_mapper_type = 'calisphere_solr.calisphere_solr'
        else:
            self.rikolti_mapper_type = rikolti_mapper_type_conversion.get(
                self.mapper_type, None)
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

    def __str__(self):
        campuses = self.campus.all()
        if campuses:
            return '{0} {1}'.format(campuses[0].slug, self.name)
        else:
            return self.name

    def get_absolute_url(self):
        return reverse('repository_collections',
                kwargs = {'repoid': self.id, 'repo_slug': str(self.slug)})

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
