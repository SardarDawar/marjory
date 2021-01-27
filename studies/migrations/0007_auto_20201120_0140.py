# Generated by Django 3.1.3 on 2020-11-19 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0006_auto_20201119_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replica',
            name='close',
            field=models.TextField(max_length=5000),
        ),
        migrations.AlterField(
            model_name='replica',
            name='consent',
            field=models.TextField(max_length=5000),
        ),
        migrations.AlterField(
            model_name='replica',
            name='invitation',
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='replica',
            name='redirect',
            field=models.TextField(max_length=5000),
        ),
        migrations.AlterField(
            model_name='replica',
            name='thanks',
            field=models.TextField(max_length=5000),
        ),
    ]