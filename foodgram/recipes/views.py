from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

# from .utils import paginator
# from .forms import PostForm, CommentForm
# from .models import Post, Group, User, Comment, Follow


# def index(request):
#     post_list = Post.objects.all().select_related(
#         'recipe'
#     )
#     context = {
#         'page_obj': paginator(request, post_list),
#     }
#     return render(request, 'posts/index.html', context)