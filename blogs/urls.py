#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('blogs.views',
    url('^$', 'index', dict(author=None, slug='teatr-masterovyie'), name='blogs_index'),
    # blog
    url('^(?P<author>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$', 'index', name='blogs_index'),
    url('^(?P<slug>[a-zA-Z0-9-]+)/$', 'index', dict(author=None), name='blogs_index'),
    # post
    url('^(?P<author>[a-zA-Z0-9-]+)/(?P<blog_slug>[a-zA-Z0-9-]+)/post/(?P<post_slug>[a-zA-Z0-9-]+)/$', 'post', name='blogs_post'),
    url('^(?P<blog_slug>[a-zA-Z0-9-]+)/post/(?P<post_slug>[a-zA-Z0-9-]+)/$', 'post', dict(author=None), name='blogs_post'),
    #
    url('^(?P<blog_pk>\d+)/(?P<post_pk>\d+)/delete/$', 'post_delete', name='blogs_post_delete'),
    url('^(?P<blog_pk>\d+)/(?P<post_pk>\d+)/edit/$', 'post_edit', name='blogs_post_edit'),
    #
    url('/post/(?P<post_pk>\d+)/comment/added/$', 'comment_added', name='blogs_comment_added'),
    url('/post/(?P<post_pk>\d+)/comment/(?P<comment_pk>\d+)/delete/$', 'comment_delete', name='blogs_comment_delete'),
)
