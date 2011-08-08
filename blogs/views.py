#coding=utf-8
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.views.generic.simple import direct_to_template

from blogs.comments import get_model
from blogs.forms import BlogPostForm
from blogs.models import Blog, BlogPost, BlogPostView
from blogs import settings
from blogs.settings import POSTS_PER_PAGE


@require_http_methods(["GET", "POST"])
@login_required
def index(request):
    start = long(request.REQUEST.get('start', 0))
    limit = long(request.REQUEST.get('limit', POSTS_PER_PAGE))
    posts = BlogPost.objects.all().order_by('-created')[start:(start+limit)]
    return direct_to_template(request,
        "blogs/index.html",
        {"posts": posts}
    )


@require_http_methods(["GET", "POST"])
@login_required
def blog_index(request, slug):
    """Содерижмое блога"""
    form = BlogPostForm(request.POST or None)
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == "POST":
        if not blog.permissions.can_post(request.user):
            return HttpResponseForbidden(u"Пользователь {0} не может постить в блог \"{1}\".".format(
                request.user.username, blog.title
            ))
        if form.is_valid():
            post = form.save(commit=False)
            post.blog = blog
            post.author = request.user
            post.save()
            form.save_m2m()
            form = BlogPostForm()
            request.flash['message'] = _(u'Пост добавлен.')

    posts = BlogPost.objects.filter(blog__pk=blog.pk).order_by('-created')[:settings.POSTS_PER_PAGE]
    return direct_to_template(request, 'blogs/blog.html', dict(
        blog=blog,
        posts=posts,
        form=form,
        user_can_post=blog.permissions.can_post(request.user)
    ))


@require_http_methods(["GET"])
@login_required
def post_delete(request, blog_pk, post_pk):
    post = get_object_or_404(BlogPost, blog__pk=blog_pk, pk=post_pk)
    if post.permissions.can_delete(request.user):
        post.delete()
        request.flash['message'] = _(u'Пост удален.')
        return redirect(post.blog.get_absolute_url())
    return HttpResponseForbidden(u"Пользователь {0} не может удалять записи из блога \"{1}\".".format(
        request.user.username,
        post.blog.title
    ))

@require_http_methods(["GET"])
@login_required
def comment_delete(request, post_pk, comment_pk):
    post = get_object_or_404(BlogPost, pk=post_pk)
    if post.permissions.can_delete_comments(request.user):
        comment = get_object_or_404(get_model(), pk=comment_pk)
        comment.delete()
        request.flash['message'] = _(u'Комментарий удален.')
        return redirect(post.get_absolute_url())
    return HttpResponseForbidden(u"Пользователь {0} не может удалять комментарии из постов блога \"{1}\".".format(
        request.user.username,
        post.blog.title
    ))


@require_http_methods(["GET", "POST"])
@login_required
def post_edit(request, blog_pk, post_pk):
    post = get_object_or_404(BlogPost, blog__pk=blog_pk, pk=post_pk)
    form = BlogPostForm(request.POST or None, instance=post)
    saved = False
    if request.method == 'POST' and form.is_valid():
        if not post.permissions.can_edit(request.user):
            return HttpResponseForbidden(
                u'Пользователь {0} не может редактировать пост \"{1}\" блога \"{2)\".'.format(
                    request.user.username,
                    post.pk,
                    post.blog.slug
                ))
        post = form.save(commit=False)
        post.save()
        form.save_m2m()
        form = BlogPostForm(instance=post)
        request.flash['message'] = _(u'Пост сохранен.')
    return direct_to_template(request, "blogs/post_edit.html", dict(
        form=form,
        post=post,
        saved=saved
    ))


def _update_post_view_time(request, post):
    view_time, created = BlogPostView.objects.get_or_create(user=request.user, post=post)
    view_time.timestamp = datetime.now()
    view_time.save()

    
@require_http_methods(["GET", "POST"])
@login_required
def post(request, blog_slug, post_pk):
    blog = get_object_or_404(Blog, slug=blog_slug)
    post = get_object_or_404(BlogPost, blog=blog, pk=post_pk)
    last_view = post.last_view(request.user)
    _update_post_view_time(request, post)
    return direct_to_template(request, "blogs/post.html", dict(
        blog=blog,
        post=post,
        last_view=last_view
    ))
