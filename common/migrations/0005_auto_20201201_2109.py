# Generated by Django 3.1.3 on 2020-12-01 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('common', '0004_auto_20201201_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='name',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Link Name'),
        ),
        migrations.AlterField(
            model_name='link',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='links', to='sites.site'),
        ),
        migrations.AlterField(
            model_name='link',
            name='url',
            field=models.URLField(max_length=500, verbose_name='Link URL'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='about_ENG',
            field=models.CharField(blank=True, max_length=2500, null=True, verbose_name='About (English)'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='about_POR',
            field=models.CharField(blank=True, max_length=2500, null=True, verbose_name='About (Portuguese)'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='tagline_ENG',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Tagline (English)'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='tagline_POR',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Tagline (Portuguese)'),
        ),
    ]
