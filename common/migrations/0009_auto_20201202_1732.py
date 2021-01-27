# Generated by Django 3.1.3 on 2020-12-02 12:32

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20201201_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='color_header_bg',
            field=colorfield.fields.ColorField(default='#417690', max_length=18, verbose_name='Header background color'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='color_nav_foot_bg',
            field=colorfield.fields.ColorField(default='#79AEC8', max_length=18, verbose_name='Nav/footer background color'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='color_nav_foot_font',
            field=colorfield.fields.ColorField(default='#FFFFFF', max_length=18, verbose_name='Nav/footer font color'),
        ),
    ]