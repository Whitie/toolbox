from functools import partial

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


FILE_ICONS = {
    'whiteboard': 'la-chalkboard',
    'chem': 'la-atom',
    'text': 'la-edit',
    'mol': 'la-atom',
}


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
