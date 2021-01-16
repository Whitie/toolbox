from django.contrib import admin

from core.models import File, FileShare, Folder, Molecule


admin.site.register(Folder)
admin.site.register(File)
admin.site.register(Molecule)
admin.site.register(FileShare)
