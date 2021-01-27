# Generated by Django 3.1.3 on 2020-11-20 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0009_auto_20201120_2340'),
        ('scripts', '0004_auto_20201120_0140'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterestedPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('contactme', models.BooleanField()),
                ('replica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interested_persons', to='studies.replica')),
            ],
            options={
                'ordering': ['replica__entrypoint'],
            },
        ),
    ]