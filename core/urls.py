from django.urls import path

from . import views


app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('whiteboard/', views.whiteboard, name='whiteboard'),
    path('whiteboard/save/', views.save_whiteboard,
         name='save_whiteboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('success/', views.success, name='success'),
    path('public/', views.public_folders, name='public_folders'),
    path('folder/<int:folder_id>/', views.folder, name='folder'),
    path('detail/<int:file_id>/', views.detail, name='detail'),
    path('add_folder/', views.add_folder, name='add_folder'),
    path('rename/<what>/', views.rename, name='rename'),
    path('download/<int:file_id>/<filetype>/', views.download,
         name='download'),
    path('download_mol/<int:mol_id>/', views.download_mol,
         name='download_mol'),
]
