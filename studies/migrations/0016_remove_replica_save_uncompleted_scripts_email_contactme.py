# Generated by Django 3.1.3 on 2020-12-01 14:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0015_auto_20201125_2120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='replica',
            name='save_uncompleted_scripts_email_contactme',
        ),
    ]
