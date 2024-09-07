from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from .forms import CommentForm
from constructions.models import Constructions


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html', status=403)


@login_required
def add_comment(request, pk):
    construction = get_object_or_404(Constructions, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.constructions = construction
        comment.save()
    return redirect('constructions:constructions_detail', pk=pk)
