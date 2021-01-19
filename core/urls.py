from django.urls import path

from . import views


app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('whiteboard/', views.whiteboard, name='whiteboard'),
    path('whiteboard/save/', views.save_whiteboard,
         name='save_whiteboard'),
    path('molecules/', views.molecules, name='molecules'),
    path('molecules/save/', views.save_molecules, name='save_molecules'),
    path('text/', views.text, name='text'),
    path('text/upload_image/', views.ck_upload_image,
         name='ck_upload_image'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('success/', views.success, name='success'),
    path('public/', views.public_folders, name='public_folders'),
    path('folder/<int:folder_id>/', views.folder, name='folder'),
    path('folder/qr/<int:folder_id>/', views.shared_folder_qrcode,
         name='folder_qr'),
    path('folder/delete/<int:folder_id>/', views.delete_folder,
         name='delete_folder'),
    path('detail/<int:file_id>/', views.detail, name='detail'),
    path('file/qr/<int:share_id>/', views.shared_file_qrcode, name='file_qr'),
    path('file/shared/<hash>/', views.shared_file, name='shared_file'),
    path('file/delete/<int:file_id>/', views.delete_file,
         name='delete_file'),
    path('add_folder/', views.add_folder, name='add_folder'),
    path('rename/<what>/', views.rename, name='rename'),
    path('download/<int:file_id>/<filetype>/', views.download,
         name='download'),
    path('download_mol/<int:mol_id>/', views.download_mol,
         name='download_mol'),
    path('change_state/<int:folder_id>/<new_state>/',
         views.change_folder_state, name='change_folder_state'),
]
