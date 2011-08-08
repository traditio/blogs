#coding=utf-8
#Author: Dmitri Patrakov <traditio@gmail.com>
#Created at 29.07.11
from django.conf.urls.defaults import *

urlpatterns = patterns('blogs.comments.views',
        url(r'^post/$', 'post_comment', name='comments-post-comment'),
)
