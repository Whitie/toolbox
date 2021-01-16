from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from qrcode import QRCode
from qrcode.image.svg import SvgPathFillImage
from weasyprint import HTML

from . import models


THUMB_SIZE = 200, 200


def is_owner_or_public(user, folder=None, file=None):
    if folder is not None:
        return folder.public or user == folder.owner
    elif file is not None:
        try:
            return user == file.owner or file.folder.public
        except Exception:
            return False
    else:
        return False


def get_item(what, id):
    model = None
    if what == 'folder':
        model = models.Folder
    elif what == 'file':
        model = models.File
    if model:
        return model.objects.get(pk=int(id))


def create_thumbnail(instance):
    _thumb = BytesIO()
    name = instance.content.name.split('/')[-1]
    instance.content.open()
    img = Image.open(instance.content)
    img.thumbnail(THUMB_SIZE)
    img.save(_thumb, format='png')
    thumb = ContentFile(_thumb.getvalue())
    instance.thumb.save(f'tn_{name}', thumb)
    instance.content.close()


def create_thumbnail_and_pdf(instance):
    name = instance.content.name.split('/')[-1]
    name = name.split('.')[0]
    instance.content.open('r')
    html = HTML(file_obj=instance.content)
    png = html.write_png()
    _pdf = html.write_pdf()
    img = Image.open(BytesIO(png))
    _thumb = BytesIO()
    img.thumbnail(THUMB_SIZE)
    img.save(_thumb, format='png')
    thumb = ContentFile(_thumb.getvalue())
    pdf = ContentFile(_pdf)
    instance.thumb.save(f'tn_{name}.png', thumb, save=False)
    instance.pdf.save(f'{name}.pdf', pdf)
    instance.content.close()


def add_js_language(req):
    lang = req.LANGUAGE_CODE
    if '-' in lang:
        lang = lang.split('-')[0]
    return dict(js_language=lang.lower())


def make_qrcode(req, relative_url):
    full_url = req.build_absolute_uri(relative_url)
    print(full_url)
    qr = QRCode(box_size=8, image_factory=SvgPathFillImage)
    qr.add_data(full_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    print(img)
    return img, 'image/svg+xml'
