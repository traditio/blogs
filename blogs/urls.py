#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('blogs.views',
    url('^$', 'index', name='blogs_index'),
    # blog
    url('^(?P<slug>[a-zA-Z0-9-]+)/$', 'blog_index', name='blogs_blog_index'),
    # post
    url('^(?P<blog_slug>[a-zA-Z0-9-]+)/(?P<post_pk>\d+)/$', 'post', name='blogs_post'),
    #
    url('^(?P<blog_pk>\d+)/(?P<post_pk>\d+)/delete/$', 'post_delete', name='blogs_post_delete'),
    url('^(?P<blog_pk>\d+)/(?P<post_pk>\d+)/edit/$', 'post_edit', name='blogs_post_edit'),
    #
    url('^post/(?P<post_pk>\d+)/comment/(?P<comment_pk>\d+)/delete/$', 'comment_delete', name='blogs_comment_delete'),
)
