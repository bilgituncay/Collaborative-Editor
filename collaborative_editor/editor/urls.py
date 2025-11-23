from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('create/', views.create_document, name='create_document'),
    path('editor/<uuid:document_id>/', views.editor, name='editor')
]