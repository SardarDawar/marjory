# Generated by Django 3.1.3 on 2020-11-17 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='image',
            order_with_respect_to='replica',
        ),
    ]
