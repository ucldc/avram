# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0006_collection_disqus_shortname'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collection',
            old_name='disqus_shortname',
            new_name='disqus_shortname_prod',
        ),
        migrations.AddField(
            model_name='collection',
            name='disqus_shortname_test',
            field=models.CharField(help_text=b'find in disqus admin', max_length=64, blank=True),
        ),
    ]
