#coding=utf-8
from django.contrib.auth.decorators import login_required
from django.http import  Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.utils.encoding import smart_unicode
from django.views.decorators.http import require_http_methods
from django.views.generic.simple import direct_to_template, redirect_to
from blogs.forms import BlogPostForm
from blogs.models import Blog, BlogPost
import settings


def get_blog(author, slug):
    blog = Blog.objects.get_by_author_slug(author, slug)
    if not blog:
        raise Http404(u"Блог %s не найден." % smart_unicode(slug))
    return blog

def redirect_to_blog(post):
    if post.blog.author:
        return redirect('blogs_index', slug=post.blog.slug, author=post.blog.author.username)
    else:
        return redirect('blogs_index', slug=post.blog.slug)



@require_http_methods(["GET", "POST"])
@login_required
def index(request, author, slug):
    """Содерижмое блога"""
    form = BlogPostForm(request.POST or None)
    blog = get_blog(author, slug)

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

    posts = BlogPost.objects.filter(blog__pk=blog.pk)[:settings.POSTS_PER_PAGE]
    return direct_to_template(request, 'blogs/blog.html', dict(
        blog=blog,
        posts=posts,
        form=form,
        user_can_post=blog.user_can_post(request.user)
    ))



def post_delete(request, blog_pk, post_pk):
    post = get_object_or_404(BlogPost, blog__pk=blog_pk, pk=post_pk)
    if post.permissions.can_delete(request.user):
        post.delete()
        return redirect_to_blog(post)
    return HttpResponseForbidden(u"Пользователь {0} не может удалять записи из блога \"{1}\".".format(
        request.user.username,
        post.blog.title
    ))
