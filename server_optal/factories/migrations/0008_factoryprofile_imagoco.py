# Generated by Django 4.2.3 on 2025-02-20 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factories', '0007_factoryprofile_visit_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='factoryprofile',
            name='imagoco',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
