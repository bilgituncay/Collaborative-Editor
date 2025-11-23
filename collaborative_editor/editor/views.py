from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Document

# Create your views here.

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