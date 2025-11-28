from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Document, DocumentCollaborator
from .forms import CustomUserCreationForm
import json

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect('document_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}. Your account has been created.')
            return redirect('document_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'editor/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def document_list(request):
    owned_documents = Document.objects.filter(created_by=request.user)
    shared_document_collabs = DocumentCollaborator.objects.filter(user=request.user).select_related('document', 'document__created_by')
    shared_documents = [(collab.document, collab.permission_level) for collab in shared_document_collabs ]

    context = {
        'owned_documents': owned_documents.order_by('-updated_at'),
        'shared_documents': shared_documents,
    }
    return render(request, 'editor/document_list.html', context)

@login_required
def create_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled')
        language = request.POST.get('language', 'python')
        doc = Document.objects.create(
            title=title,
            language=language,
            created_by=request.user
        )
        return redirect('editor', document_id=doc.id)
    return render(request, 'editor/create_document.html')

@login_required
def editor(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if not document.has_permission(request.user):
        messages.error(request, 'You do not have permission to access this document.')
        return redirect('document_list')
    
    permission_level = document.get_permission_level(request.user)
    is_owner = document.created_by == request.user

    return render(request, 'editor/editor.html', {
        'document': document,
        'document_id': str(document.id),
        'permission_level': permission_level,
        'is_owner': is_owner,
        'can_edit': permission_level in ['owner', 'edit']
    })

@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if document.created_by != request.user:
        messages.error(request, 'You do not have permission to delete this document.')
        return redirect(document_list)
    
    if request.method == 'POST':
        title = document.title
        document.delete()
        messages.success(request, f'Document "{title}"deleted successfully.')
        return redirect('document_list')
    
    return render(request, 'editor/delete_confirm.html', {'document': document})

@login_required
def manage_collaborators(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if document.created_by != request.user:
        messages.error(request, 'You do not have permission to manage collaborators.')
        return redirect('document_list')
    
    collaborators = document.collaborators.select_related('user').all()

    return render(request, 'editor/manage_collaborators.html', {
        'document': document,
        'collaborators': collaborators
    })

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]

    user_list = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.get_full_name() or user.username
    } for user in users]

    return JsonResponse({'users': user_list})

@login_required
def add_collaborator(request, document_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    document = get_object_or_404(Document, id=document_id)

    if document.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        permission_level = data.get('permission_level', 'view')

        user = User.objects.get(id=user_id)

        if user == document.created_by:
            return JsonResponse({'error': 'Cannot add document owner as collaborator'}, status=400)
        
        collaborator, created = DocumentCollaborator.objects.get_or_create(
            document=document,
            user=user,
            defaults={
                'permission_level': permission_level,
                'added_by': request.user
            }
        )

        if not created:
            collaborator.permission_level = permission_level
            collaborator.save()


        action = 'added' if created else 'updated'
        messages.success(request, f'{user.username} has been {action} as a collaborator.')

        return JsonResponse({
            'success': True,
            'message': f'{user.username} {action} successfully',
            'collaborator': {
                'id': collaborator.id,
                'username': user.username,
                'permission_level': collaborator.permission_level
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def remove_collaborator(request, document_id, collaborator_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('document_list')
    
    document = get_object_or_404(Document, id=document_id)
    collaborator = get_object_or_404(DocumentCollaborator, id=collaborator_id, document=document)

    if document.created_by != request.user:
        messages.error(request, 'You do not have permission to remove collaborators.')
        return redirect('document_list')
    
    username = collaborator.user.username
    collaborator.delete()
    messages.success(request, f'{username} has been removed from collaborators.')

    return redirect('manage_collaborators', document_id=document_id)
    

@login_required
def update_collaborator_permission(request, document_id, collaborator_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    document = get_object_or_404(Document, id=document_id)
    collaborator = get_object_or_404(DocumentCollaborator, id=collaborator_id, document=document)

    if document.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        permission_level = data.get('permission_level')
        
        if permission_level not in ['view', 'edit']:
            return JsonResponse({'error': 'Invalid permission level'}, status=400)
        
        collaborator.permission_level = permission_level
        collaborator.save()

        return JsonResponse({
            'success': True,
            'message': f'Permission updated to {permission_level}'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)