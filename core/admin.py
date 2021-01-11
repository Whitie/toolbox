from django.contrib import admin

from core.models import File, Folder, Molecule


admin.site.register(Folder)
admin.site.register(File)
admin.site.register(Molecule)
