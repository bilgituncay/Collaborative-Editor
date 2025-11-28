from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('register/', views.register, name='register'),
    path('create/', views.create_document, name='create_document'),
    path('editor/<uuid:document_id>/', views.editor, name='editor'),
    path('delete/<uuid:document_id>/', views.delete_document, name='delete_document'),
    path('collaborators/<uuid:document_id>/', views.manage_collaborators, name='manage_collaborators'),
    path('api/search-users/', views.search_users, name='search_users'),
    path('api/add-collaborator/<uuid:document_id>/', views.add_collaborator, name='add_collaborator'),
    path('api/remove-collaborator/<uuid:document_id>/<int:collaborator_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('api/update-permission/<uuid:document_id>/<int:collaborator_id>/', views.update_collaborator_permission, name='update_collaborator_permission')
]