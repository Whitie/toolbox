from django.db.models.signals import post_save
from django_q.tasks import async_task

from .models import File


def create_thumbnail(sender, instance, created, **kw):
    if created:
        if instance.type == 'text':
            async_task('core.utils.create_thumbnail_and_pdf', instance)
        else:
            async_task('core.utils.create_thumbnail', instance)


def connect_all():
    post_save.connect(create_thumbnail, sender=File,
                      dispatch_uid='toolbox-thumb-creation')
    print('Signals connected')
