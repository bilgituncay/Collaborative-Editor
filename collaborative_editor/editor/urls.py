from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('register/', views.register, name='register'),
    path('create/', views.create_document, name='create_document'),
    path('editor/<uuid:document_id>/', views.editor, name='editor'),
    path('delete/<uuid:document_id>/', views.delete_document, name='delete_document'),

]