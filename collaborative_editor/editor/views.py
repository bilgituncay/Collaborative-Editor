from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Document
from .forms import CustomUserCreationForm

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

def user_login(request):
    pass

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def document_list(request):
    documents = Document.objects.filter(created_by=request.user).order_by('-updated_at')
    return render(request, 'editor/document_list.html', {'documents': documents})

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
    return render(request, 'editor/editor.html', {
        'document': document,
        'document_id': str(document.id)
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