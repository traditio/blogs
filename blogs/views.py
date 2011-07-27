#coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import  Http404, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.views.generic.simple import direct_to_template
from threadedcomments.models import ThreadedComment

from blogs.forms import BlogPostForm
from blogs.models import Blog, BlogPost
from blogs import settings


def get_blog_or_404(author, slug):
    blog = Blog.objects.get_by_author_slug(author, slug)
    if not blog:
        raise Http404(u"Блог %s не найден." % smart_unicode(slug))
    return blog


@require_http_methods(["GET", "POST"])
@login_required
def index(request, author, slug):
    """Содерижмое блога"""
    form = BlogPostForm(request.POST or None)
    blog = get_blog_or_404(author, slug)

    if request.method == "POST":
        if not blog.user_can_post(request.user):
            return HttpResponseForbidden(u"Пользователь {0} не может постить в блог \"{1}\".".format(
                request.user.username, blog.title
            ))
        if form.is_valid():
            post = form.save(commit=False)
            post.blog = blog
            post.save()
            form.save_m2m()
            form = BlogPostForm()
            request.flash['message'] = _(u'Пост добавлен.')

    posts = BlogPost.objects.filter(blog__pk=blog.pk)[:settings.POSTS_PER_PAGE]
    return direct_to_template(request, 'blogs/blog.html', dict(
        blog=blog,
        posts=posts,
        form=form,
        user_can_post=blog.user_can_post(request.user)
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
        comment = get_object_or_404(ThreadedComment, pk=comment_pk)
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
                    post.slug,
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


@require_http_methods(["GET", "POST"])
@login_required
def post(request, author, blog_slug, post_slug):
    blog = get_blog_or_404(author, blog_slug)
    post = get_object_or_404(BlogPost, blog=blog, slug=post_slug)
    return direct_to_template(request, "blogs/post.html", dict(
        blog=blog,
        post=post,
        ))


@require_http_methods(["GET"])
def comment_added(request, post_pk):
    post = get_object_or_404(BlogPost, pk=post_pk)
    request.flash['message'] = _(u'Комментарий добавлен.')
    return redirect(post.get_absolute_url())