# Generated by Django 3.1.5 on 2021-01-16 11:11

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210109_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(editable=False, max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('valid_until', models.DateTimeField(default=core.models.valid_7d, verbose_name='Valid until')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shares', to='core.file', verbose_name='File')),
            ],
            options={
                'verbose_name': 'File Share',
                'verbose_name_plural': 'File Shares',
                'ordering': ['file', '-created'],
            },
        ),
    ]
