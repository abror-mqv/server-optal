# Generated by Django 4.2.3 on 2025-02-17 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factories', '0004_alter_colorvariation_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='factoryprofile',
            name='supplier_id',
            field=models.CharField(default=0, editable=False, max_length=6, unique=True),
            preserve_default=False,
        ),
    ]
