#coding=utf-8
from functools import partial
from datetime import datetime
from annoying.functions import get_object_or_None
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Sum
from django.http import HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.views.generic.simple import direct_to_template

from blogs.comments import get_model
from blogs.forms import BlogPostForm
from blogs.models import Blog, BlogPost, BlogPostView
from blogs import settings
from blogs.settings import POSTS_PER_PAGE
from ratings.models import RatedItem

def add_rating_score(qs):
    ids = [c.id for c in qs]
    obj_for_content_type = qs[0] if isinstance(qs, (list, tuple)) else qs.model
    content_type = ContentType.objects.get_for_model(obj_for_content_type)
    scores = dict(RatedItem.objects.filter(content_type__id=content_type.id, object_id__in=ids).values_list('object_id').annotate(Sum('score')))
    for obj in qs:
        obj._cached_rating_score = scores.get(obj.id) or 0
    return qs

def new_comments_count(posts_qs, user):
    posts_ids = [post.pk for post in posts_qs]
    try:
        views = dict((v.post_id, v) for v in list(BlogPostView.objects.filter(post__id__in=posts_ids, user=user)))
    except:
        raise ValueError
    print 'views', views
    for post in posts_qs:
        view = views.get(post.id)
        if view is None:
            print 'post id = ', post.id, 'view = ', view
            post.new_comments_count = post.comments_count
        else:
            post.new_comments_count = post.comments.filter(submit_date__gte=view.timestamp).count()
        print 'post id = ', post.id, 'new_comments_count = ', post.new_comments_count

@require_http_methods(["GET", "POST"])
@login_required
def index(request):
    start = long(request.REQUEST.get('start', 0))
    limit = long(request.REQUEST.get('limit', POSTS_PER_PAGE))
    add_new_comments_count = partial(new_comments_count, user=request.user)
    posts = BlogPost.objects.select_related('author__id', 'last_view_objs', 'blog__id').all().order_by('-created').transform(add_new_comments_count)[start:(start+limit)]
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

    add_new_comments_count = partial(new_comments_count, user=request.user)
    posts = BlogPost.objects.select_related('user__id', 'blog__id').filter(blog__pk=blog.pk).order_by('-created').transform(add_new_comments_count).transform(add_rating_score)[:settings.POSTS_PER_PAGE]

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
    try:
        post = BlogPost.objects.select_related('blog__id', 'user').get(blog=blog, pk=post_pk)
    except BlogPost.DoesNotExist:
        raise Http404()
    view = get_object_or_None(BlogPostView, post__id=post.id, user=request.user)
    if view is None:
        post.new_comments_count = post.comments_count
    else:
        post.new_comments_count = post.comments.filter(submit_date__gte=view.timestamp).count()
    last_view = post.last_view(request.user)
    _update_post_view_time(request, post)

    return direct_to_template(request, "blogs/post.html", dict(
        blog=blog,
        post=post,
        last_view=last_view,
        comment_list=list(add_rating_score(post.comments.select_related('user')))
    ))

@require_http_methods(["GET"])
@login_required
def search(request):
    if not request.GET.get('q'):
        return HttpResponseBadRequest('400 Empty search query.')
    query = request.GET.get('q')
    queryset = BlogPost.search.query(query)
    count = queryset.count()
    return direct_to_template(request,
        "blogs/search_results.html",
        dict(q=query, count=count, results=queryset)
    )
