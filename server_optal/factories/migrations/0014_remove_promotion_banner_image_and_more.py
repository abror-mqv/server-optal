# Generated by Django 4.2.3 on 2025-03-11 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('factories', '0013_promotion_promotionapplication_productpromotion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotion',
            name='banner_image',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='promotion',
            name='start_date',
        ),
    ]
