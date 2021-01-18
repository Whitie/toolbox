# Generated by Django 3.1.5 on 2021-01-18 09:51

import core.models
from django.db import migrations, models
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_ckuploadimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ckuploadimage',
            name='upload',
            field=models.FileField(upload_to=functools.partial(core.models.user_directory_path, *(), **{'subpath': 'ck_images'})),
        ),
    ]
