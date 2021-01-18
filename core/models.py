from datetime import timedelta
from functools import partial
from hashlib import sha256

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


FILE_ICONS = {
    'whiteboard': 'la-chalkboard',
    'chem': 'la-atom',
    'text': 'la-edit',
    'mol': 'la-atom',
}


def valid_7d():
    now = timezone.now()
    return now + timedelta(days=7)


def user_directory_path(instance, filename, subpath=''):
    path = f'uploads/user_{instance.owner.id:04d}'
    if subpath:
        return f'{path}/{subpath}/{filename}'
    return f'{path}/{instance.type}/{filename}'


class Folder(models.Model):
    name = models.CharField(_('Folder'), max_length=50)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Owner'),
        related_name='folders'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, verbose_name=_('Parent'),
        related_name='subfolders', blank=True, null=True, default=None
    )
    public = models.BooleanField(_('Public'), blank=True, default=False)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.owner.username}'

    def get_parents(self):
        parents = []
        parent = self.parent
        while parent is not None:
            parents.append((parent.id, parent.name))
            parent = parent.parent
        return parents

    def breadcrumbs(self):
        parents = list(reversed(self.get_parents()))
        parents.append((self.id, self.name))
        return parents

    class Meta:
        verbose_name = _('Folder')
        verbose_name_plural = _('Folders')
        ordering = ['owner', 'name']


class File(models.Model):

    class Type(models.TextChoices):
        WHITEBOARD = 'whiteboard', _('Whiteboard')
        CHEMICAL = 'chem', _('Chemical Drawing')
        TEXT = 'text', _('Text Document')

    name = models.CharField(_('Name'), max_length=100)
    type = models.CharField(_('Type'), max_length=10, choices=Type.choices)
    content = models.FileField(_('Content'), upload_to=user_directory_path)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Owner'),
        related_name='files'
    )
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, verbose_name=_('Folder'),
        related_name='files', blank=True, null=True, default=None
    )
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    thumb = models.ImageField(
        _('Thumbnail'), blank=True, null=True, default=None,
        upload_to=partial(user_directory_path, subpath='thumbs')
    )
    # only set for type text
    pdf = models.ImageField(
        _('PDF'), blank=True, null=True, default=None,
        upload_to=partial(user_directory_path, subpath='pdf')
    )

    def __str__(self):
        return self.name

    @property
    def mimetype(self):
        if self.type == 'text':
            return 'text/html', '.html'
        return 'image/png', '.png'

    @property
    def icon(self):
        return FILE_ICONS[self.type]

    def has_molecules(self):
        return bool(self.molecules.all().count())

    def get_sdf(self):
        sdf = '\n\n$$$$\n\n'.join(
            self.molecules.all().values_list('content', flat=True)
        )
        return 'chemical/x-mdl-sdfile', '.sdf', sdf

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        ordering = ['owner', 'name']


class Molecule(models.Model):
    name = models.CharField(_('Name'), max_length=150, blank=True)
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, verbose_name=_('File'),
        related_name='molecules'
    )
    content = models.TextField(_('Content'))

    mimetype = 'chemical/x-mdl-molfile', '.mol'

    def __str__(self):
        if self.name:
            return self.name
        return self.file.name

    class Meta:
        verbose_name = _('Molecule')
        verbose_name_plural = _('Molecules')
        ordering = ['name']


class FileShare(models.Model):
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, verbose_name=_('File'),
        related_name='shares'
    )
    hash = models.CharField(editable=False, max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(_('Valid until'), default=valid_7d)

    def save(self, *args, **kw):
        now = str(timezone.now())
        filename = str(self.file)
        self.hash = sha256(f'{now}{filename}'.encode('utf-8')).hexdigest()
        super().save(*args, **kw)

    class Meta:
        verbose_name = _('File Share')
        verbose_name_plural = _('File Shares')
        ordering = ['file', '-created']


class CKUploadImage(models.Model):
    upload = models.FileField(
        upload_to=partial(user_directory_path, subpath='ck_images')
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('Owner')
    )
