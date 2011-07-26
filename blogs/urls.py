#coding=utf-8
#--- Author: Dmitri Patrakov <traditio@gmail.com>
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('blogs.views',
    url('^$', 'index', dict(author=None, slug='teatr-masterovyie'), name='blogs_index'),
    url('^(?P<author>[a-zA-Z0-9-]+)/(?P<slug>[a-zA-Z0-9-]+)/$', 'index', name='blogs_index'),
    url('^(?P<slug>[a-zA-Z0-9-]+)/$', 'index', dict(author=None), name='blogs_index'),
    url('^(?P<blog_pk>\d+)/(?P<post_pk>\d+)/delete/$', 'post_delete', name='blogs_post_delete'),
)
