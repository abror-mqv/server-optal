# Generated by Django 4.2.3 on 2025-01-08 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_order_city_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='city_delivery',
            field=models.CharField(default='Город не указан', max_length=256),
        ),
    ]
