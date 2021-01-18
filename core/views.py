import json

from django.contrib import messages
from django.contrib.auth import (
    authenticate, login as django_login, logout as django_logout
)
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import get_valid_filename
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import forms, utils
from .models import CKUploadImage, File, FileShare, Folder, Molecule


def index(req):
    req.session['folder'] = None
    if req.user.is_authenticated:
        folders = Folder.objects.filter(owner=req.user, parent=None)
        files = File.objects.filter(owner=req.user, folder=None)
        ctx = dict(folders=folders, files=files, folder=None)
        return render(req, 'core/index.html', ctx)
    form = forms.LoginForm()
    return render(req, 'core/start.html', {'form': form})


def public_folders(req):
    req.session['folder'] = None
    folders = Folder.objects.filter(public=True)
    ctx = dict(folder=None, folders=folders)
    return render(req, 'core/public_folders.html', ctx)


def login(req):
    form = forms.LoginForm(req.POST)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(req, username=cd['username'],
                            password=cd['password'])
        if user is not None:
            django_login(req, user)
            messages.success(req, _('Login successfull'))
        else:
            messages.error(req, _('Wrong credentials'))
    else:
        messages.error(req, _('Please fill the form'))
    return redirect('core:index')


def logout(req):
    django_logout(req)
    return redirect('core:success')


def success(req):
    return render(req, 'core/success.html')


@require_POST
def add_folder(req):
    form = forms.NewFolderForm(req.POST)
    folder = utils.get_folder(req)
    if form.is_valid():
        folder = Folder(owner=req.user, parent=folder, **form.cleaned_data)
        folder.save()
        return HttpResponse('ok')
    return HttpResponse('invalid')


def folder(req, folder_id):
    folder = Folder.objects.select_related().get(pk=folder_id)
    req.session['folder'] = folder.id
    if not utils.is_owner_or_public(req.user, folder=folder):
        return HttpResponseForbidden()
    query = Q(public=True)
    if req.user.is_authenticated:
        query |= Q(owner=req.user)
    ctx = dict(folder=folder, folders=folder.subfolders.filter(query),
               files=folder.files.all())
    return render(req, 'core/folder.html', ctx)


@login_required
def whiteboard(req):
    folder = utils.get_folder(req)
    return render(req, 'core/whiteboard.html', {'folder': folder})


@login_required
@require_POST
def save_whiteboard(req):
    form = forms.NewFileForm(req.POST, req.FILES)
    folder = utils.get_folder(req)
    if form.is_valid():
        file = File(owner=req.user, type='whiteboard', folder=folder,
                    **form.cleaned_data)
        file.save()
        return HttpResponse('ok')
    return HttpResponse('invalid')


@login_required
def molecules(req):
    folder = utils.get_folder(req)
    return render(req, 'core/molecules2.html', {'folder': folder})


@login_required
@require_POST
def save_molecules(req):
    data = json.loads(req.body)
    folder = utils.get_folder(req)
    filename = get_valid_filename(f'{data["name"]}.png')
    png = utils.get_kekule_image(data['image'])
    file = File(owner=req.user, type='chem', name=data['name'],
                folder=folder)
    file.content.save(filename, png)
    for num, mol in enumerate(data['molecules'], start=1):
        molecule = Molecule(name=f'{file.name} {num:03d}', content=mol,
                            file=file)
        molecule.save()
    return HttpResponse('ok')


@require_POST
def rename(req, what):
    item = utils.get_item(what, req.POST['id'])
    if not item or item.owner != req.user:
        return HttpResponse(_('Aborted'))
    max_length = item._meta.get_field('name').max_length
    item.name = req.POST['name'][:max_length]
    item.save()
    return HttpResponse('ok')


def detail(req, file_id, shared=False):
    file = File.objects.select_related().get(pk=file_id)
    if not shared and not utils.is_owner_or_public(req.user, file=file):
        return HttpResponseForbidden()
    if req.method == 'POST':
        action = req.POST.get('share')
        utils.manage_share(file, action)
    if file.type == 'text':
        tpl = 'text'
    else:
        tpl = 'image'
    ctx = dict(file=file, shared=shared)
    ctx['share'] = FileShare.objects.filter(file=file).last()
    return render(req, f'core/detail_{tpl}.html', ctx)


def shared_file(req, hash):
    share = get_object_or_404(FileShare, hash=hash)
    return detail(req, share.file.id, shared=True)


def download(req, file_id, filetype):
    file = File.objects.select_related().get(pk=file_id)
    if not utils.is_owner_or_public(req.user, file=file):
        return HttpResponseForbidden()
    name = get_valid_filename(file.name)
    if filetype == 'pdf':
        content = file.pdf.read()
        mimetype, ext = 'application/pdf', '.pdf'
    elif filetype in ('html', 'png'):
        content = file.content.read()
        mimetype, ext = file.mimetype
    elif filetype == 'sdf':
        mimetype, ext, content = file.get_sdf()
    else:
        return HttpResponseForbidden()
    response = HttpResponse(content, content_type=mimetype)
    response['Content-Disposition'] = f'attachment; filename={name}{ext}'
    return response


def download_mol(req, mol_id):
    mol = Molecule.objects.get(pk=mol_id)
    if mol.name:
        name = get_valid_filename(mol.name)
    else:
        name = f'molecule_{mol_id:04d}'
    mimetype, ext = mol.mimetype
    response = HttpResponse(mol.content, content_type=mimetype)
    response['Content-Disposition'] = f'attachment; filename={name}{ext}'
    return response


def shared_folder_qrcode(req, folder_id):
    url = reverse('core:folder', args=(folder_id,))
    img, ct = utils.make_qrcode(req, url)
    response = HttpResponse(content_type=ct)
    img.save(response)
    return response


def shared_file_qrcode(req, share_id):
    url = reverse('core:shared_file', args=(share_id,))
    img, ct = utils.make_qrcode(req, url)
    response = HttpResponse(content_type=ct)
    img.save(response)
    return response


def change_folder_state(req, folder_id, new_state):
    folder = Folder.objects.get(pk=folder_id)
    if folder.owner != req.user:
        return HttpResponseForbidden()
    if new_state == 'public':
        folder.public = True
    else:
        folder.public = False
    folder.save()
    return HttpResponse('ok')


@login_required
def text(req):
    folder = utils.get_folder(req)
    if req.method == 'POST':
        form = forms.EditorForm(req.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = get_valid_filename(cd['name'])
            html = utils.HTML_SKELETON.format(title=cd['name'],
                                              body=cd['editor'])
            content = ContentFile(html.encode('utf-8'), f'{name}.html')
            file = File(owner=req.user, type='text', name=cd['name'],
                        folder=folder, content=content)
            file.save()
            if folder:
                return redirect('core:folder', folder_id=folder.id)
            return redirect('core:index')
    ctx = dict(folder=folder)
    return render(req, 'core/text.html', ctx)


@require_POST
@csrf_exempt
def ck_upload_image(req):
    ck = CKUploadImage(owner=req.user)
    form = forms.CKUploadImageForm(req.POST, req.FILES, instance=ck)
    if form.is_valid():
        form.save()
        data = {
            'fileName': ck.upload.name.split('/')[-1],
            'uploaded': 1,
            'url': req.build_absolute_uri(ck.upload.url),
        }
        return JsonResponse(data)
    data = {
        'uploaded': 0,
        'error': {'message': ' '.join(form.errors)}
    }
    return JsonResponse(data)
